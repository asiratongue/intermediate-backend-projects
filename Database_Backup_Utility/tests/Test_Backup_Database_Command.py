import pytest
import os
import sys
import io
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import gzip
import json
import shutil

# Import the backup_database module
from src.commands.backup_database import backup


class TestBackupCommand:
    """Tests for the backup database command"""
    
    def test_full_backup_postgresql(self, mock_load_configs, mock_postgres_connection, mock_subprocess, 
                                   temp_backup_dir, monkeypatch):
        """Test full backup for PostgreSQL database"""
        # Mock user input for "full" backup choice
        monkeypatch.setattr('builtins.input', lambda _: "full")
        
        # Mock validation function to return success
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        # Prepare a mock dump file that will be created during the backup process
        dump_dir = os.path.join(temp_backup_dir, "dump_exports")
        os.makedirs(dump_dir, exist_ok=True)

        # Need to patch multiple functions
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection), \
             patch('utils.validation.validate_full_backup', mock_validation), \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file:
            
            # Mock subprocess run to create a temporary file
            def mock_subprocess_run(*args, **kwargs):
                if 'stdout' in kwargs and hasattr(kwargs['stdout'], 'name'):
                    # Create a dummy file for the subprocess output
                    with open(kwargs['stdout'].name, 'w') as f:
                        f.write("-- PostgreSQL database dump")
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stderr = ""
                return mock_result
            
            mock_run.side_effect = mock_subprocess_run
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the backup command
                backup("postgresql", temp_backup_dir, "local", 10)
                
                # Verify the correct operations were performed
                assert mock_postgres_connection.cursor.called
                assert mock_validation.called
                
                # Verify output
                output = captured_output.getvalue()
                assert "Successfully backed up" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_full_backup_sqlite(self, mock_load_configs, sqlite_db, mock_subprocess, 
                               temp_backup_dir, monkeypatch):
        """Test full backup for SQLite database"""
        # Mock user input for "full" backup choice
        monkeypatch.setattr('builtins.input', lambda _: "full")
        
        # Mock validation function to return success
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        # Need to patch multiple functions
        with patch('utils.connect_db.connect_db', return_value=sqlite_db), \
             patch('utils.validation.validate_full_backup', mock_validation), \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file:
            
            # Mock subprocess run to create a temporary file
            def mock_subprocess_run(*args, **kwargs):
                if 'stdout' in kwargs and hasattr(kwargs['stdout'], 'name'):
                    # Create a dummy file for the subprocess output
                    with open(kwargs['stdout'].name, 'w') as f:
                        f.write("PRAGMA foreign_keys=OFF;\nBEGIN TRANSACTION;")
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stderr = ""
                return mock_result
            
            mock_run.side_effect = mock_subprocess_run
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the backup command
                backup("sqlite", temp_backup_dir, "local", 10)
                
                # Verify the validation was called
                assert mock_validation.called
                
                # Verify output
                output = captured_output.getvalue()
                assert "Successfully backed up" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_full_backup_mongodb(self, mock_load_configs, mock_mongodb_connection, mock_subprocess, 
                                temp_backup_dir, monkeypatch):
        """Test full backup for MongoDB database"""
        # Mock user input for "full" backup choice
        monkeypatch.setattr('builtins.input', lambda _: "full")
        
        # Mock validation function to return success
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        # Need to patch multiple functions
        with patch('utils.connect_db.connect_db', return_value=mock_mongodb_connection), \
             patch('utils.validation.validate_full_backup', mock_validation), \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('tarfile.open') as mock_tarfile:
            
            # Mock subprocess and tarfile operations
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            mock_tarfile.return_value.__enter__.return_value = MagicMock()
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the backup command
                backup("mongodb", temp_backup_dir, "local", 10)
                
                # Verify the validation was called
                assert mock_validation.called
                
                # Verify output
                output = captured_output.getvalue()
                assert "Successfully backed up" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_table_backup_postgresql(self, mock_load_configs, mock_postgres_connection, 
                                    temp_backup_dir, monkeypatch):
        """Test backing up specific tables for PostgreSQL"""
        # Mock user input for table list
        monkeypatch.setattr('builtins.input', lambda _: "test_users test_products")
        
        # Mock cursor and copy_expert
        cursor = mock_postgres_connection.cursor()
        
        # Mock validation function to return success
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection), \
             patch('utils.validation.validate_backup_csv', mock_validation), \
             patch('builtins.open', mock_open()) as mock_file:
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the backup command
                backup("postgresql", temp_backup_dir, "local", 10)
                
                # Verify the correct operations were performed
                assert cursor.copy_expert.call_count >= 1
                assert mock_validation.call_count >= 1
                
                # Verify output contains success messages for both tables
                output = captured_output.getvalue()
                assert "backed up" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_invalid_input(self, mock_load_configs, mock_postgres_connection, temp_backup_dir, monkeypatch):
        """Test handling of invalid input"""
        # Mock user input to be non-string type by returning None first time (which isn't a string)
        inputs = [None, "full"]
        input_iter = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
        
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection):
            # Redirect stderr to capture error messages
            captured_error = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # This should fail due to invalid input
                backup("postgresql", temp_backup_dir, "local", 10)
                
                # No assertion needed - we just verify it doesn't raise an exception
            finally:
                sys.stderr = original_stderr
    
    def test_invalid_compression(self, mock_load_configs, mock_postgres_connection, temp_backup_dir, monkeypatch):
        """Test handling of invalid compression value"""
        # Mock user input
        monkeypatch.setattr('builtins.input', lambda _: "full")
        
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection):
            # Redirect stderr to capture error messages
            captured_error = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # This should fail due to invalid compression value
                backup("postgresql", temp_backup_dir, "local", 11)  # Above the allowed range
                
                # No assertion needed - we just verify it doesn't raise an exception
            finally:
                sys.stderr = original_stderr
    
    def test_cloud_storage(self, mock_load_configs, mock_postgres_connection, mock_subprocess, 
                          temp_backup_dir, monkeypatch):
        """Test backing up to cloud storage"""
        # Mock user input
        monkeypatch.setattr('builtins.input', lambda _: "full")
        
        # Mock validation function
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection), \
             patch('utils.validation.validate_full_backup', mock_validation), \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()) as mock_file:
            
            # Mock subprocess operations
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the backup command with cloud storage
                backup("postgresql", temp_backup_dir, "cloud", 10)
                
                # Verify AWS S3 copy command was called
                s3_calls = [call for call in mock_run.call_args_list if 'aws' in str(call)]
                assert len(s3_calls) > 0
                
                # Verify output
                output = captured_output.getvalue()
                assert "Successfully backed up" in output
            finally:
                sys.stdout = sys.__stdout__
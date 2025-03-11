import pytest
import os
import sys
import io
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil
import subprocess

# Import application modules
from src.main import app
from src.config import config_manager
from src.utils.connect_db import connect_db
from src.commands import backup_database, connection_test, restore_database, view_database, delete_backup


class TestCommandLineInterface:
    """Integration tests for the command line interface"""
    
    def test_cli_connection_test(self, mock_load_configs, mock_postgres_connection):
        """Test the test-connection CLI command"""
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection):
            # Use typer's testing utilities to invoke the command
            runner = app
            
            with patch.object(sys, 'argv', ['main.py', 'test-connection', 'postgresql']):
                # Capture stdout to verify output
                captured_output = io.StringIO()
                sys.stdout = captured_output
                
                try:
                    # We can't actually run the app without typer's testing utilities,
                    # so we'll call the function directly
                    connection_test.connection_test("postgresql")
                    
                    # Verify output
                    output = captured_output.getvalue()
                    expected_message = f"connection to {mock_load_configs['postgresql']['database']} is ok!"
                    assert expected_message in output
                finally:
                    sys.stdout = sys.__stdout__
    
    def test_cli_view(self, mock_load_configs, mock_postgres_connection):
        """Test the view CLI command"""
        # Mock the cursor
        cursor = mock_postgres_connection.cursor()
        cursor.fetchall.return_value = [('test_users',), ('test_products',)]
        
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection):
            # Use typer's testing utilities to invoke the command
            runner = app
            
            with patch.object(sys, 'argv', ['main.py', 'view', 'postgresql']):
                # Capture stdout to verify output
                captured_output = io.StringIO()
                sys.stdout = captured_output
                
                try:
                    # Call the function directly
                    view_database.view("postgresql")
                    
                    # Verify output
                    output = captured_output.getvalue()
                    assert "table name:  test_users" in output
                    assert "table name:  test_products" in output
                finally:
                    sys.stdout = sys.__stdout__
    
    def test_backup_restore_workflow(self, mock_load_configs, mock_postgres_connection, 
                                    mock_subprocess, monkeypatch, tmp_path):
        """Test a complete backup and restore workflow"""
        # Set up temporary directories
        temp_backup_dir = tmp_path / "backups"
        temp_backup_dir.mkdir(exist_ok=True)
        dump_dir = temp_backup_dir / "dump_exports"
        dump_dir.mkdir(exist_ok=True)
        
        # Mock file paths
        backup_file_path = dump_dir / "test_backup.sql"
        
        # Mock user inputs for backup command
        backup_inputs = ["full", "Y"]
        restore_inputs = ["d", str(backup_file_path), "Y"]
        all_inputs = iter(backup_inputs + restore_inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(all_inputs))
        
        # Mock validation function to return success
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        # Need to patch multiple functions for this integration test
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection), \
             patch('utils.validation.validate_full_backup', mock_validation), \
             patch('subprocess.run') as mock_run, \
             patch('builtins.open', MagicMock()), \
             patch('os.makedirs', MagicMock(return_value=None)):
            
            # Mock subprocess operations
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            
            # Create a backup list file
            backup_list_file = Path(mock_load_configs["test_config_dir"], "db_backup_list.txt")
            backup_list_file.write_text(f"postgresql  {backup_file_path}\n")
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Step 1: Create a backup
                backup_database.backup("postgresql", str(temp_backup_dir), "local", 10)
                
                # Step 2: Restore the backup
                restore_database.restore("postgresql")
                
                # Verify output
                output = captured_output.getvalue()
                assert "Successfully backed up" in output
                assert "restored successfully" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_backup_delete_workflow(self, mock_load_configs, mock_postgres_connection, 
                                   mock_subprocess, monkeypatch, tmp_path):
        """Test a complete backup and delete workflow"""
        # Set up temporary directories
        temp_backup_dir = tmp_path / "backups"
        temp_backup_dir.mkdir(exist_ok=True)
        dump_dir = temp_backup_dir / "dump_exports"
        dump_dir.mkdir(exist_ok=True)
        
        # Mock file paths
        backup_file_path = dump_dir / "test_backup.sql"
        # Create a dummy file
        backup_file_path.write_text("-- PostgreSQL dump")
        
        # Mock user inputs for backup command
        backup_inputs = ["full", "Y"]
        delete_inputs = ["d", str(backup_file_path)]
        all_inputs = iter(backup_inputs + delete_inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(all_inputs))
        
        # Mock validation function to return success
        mock_validation = MagicMock(return_value=(True, "Validation passed"))
        
        # Need to patch multiple functions for this integration test
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection), \
             patch('utils.validation.validate_full_backup', mock_validation), \
             patch('subprocess.run') as mock_run, \
             patch('os.remove', MagicMock()):
            
            # Mock subprocess operations
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            
            # Create a backup list file
            backup_list_file = Path(mock_load_configs["test_config_dir"], "db_backup_list.txt")
            backup_list_file.write_text(f"postgresql  {backup_file_path}\n")
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Step 1: Create a backup
                backup_database.backup("postgresql", str(temp_backup_dir), "local", 10)
                
                # Step 2: Delete the backup
                delete_backup.delete()
                
                # Verify output
                output = captured_output.getvalue()
                assert "Successfully backed up" in output
                assert "sucessfully deleted" in output
            finally:
                sys.stdout = sys.__stdout__
                

class TestDatabaseConnections:
    """Integration tests for database connections"""
    
    def test_postgres_config_loading(self, mock_load_configs):
        """Test loading PostgreSQL configurations"""
        configs = config_manager.load_configs()
        
        # Verify PostgreSQL config
        assert "postgresql" in configs
        assert configs["postgresql"]["type"] == "postgresql"
        assert "host" in configs["postgresql"]
        assert "port" in configs["postgresql"]
        assert "database" in configs["postgresql"]
        assert "user" in configs["postgresql"]
        assert "password" in configs["postgresql"]
    
    def test_sqlite_config_loading(self, mock_load_configs):
        """Test loading SQLite configurations"""
        configs = config_manager.load_configs()
        
        # Verify SQLite config
        assert "sqlite" in configs
        assert configs["sqlite"]["type"] == "sqlite"
        assert "path" in configs["sqlite"]
        assert "database" in configs["sqlite"]
    
    def test_mongodb_config_loading(self, mock_load_configs):
        """Test loading MongoDB configurations"""
        configs = config_manager.load_configs()
        
        # Verify MongoDB config
        assert "mongodb" in configs
        assert configs["mongodb"]["type"] == "mongodb"
        assert "host" in configs["mongodb"]
        assert "database" in configs["mongodb"]
        assert "connection_string" in configs["mongodb"]
    
    def test_s3_config_loading(self, mock_load_configs):
        """Test loading S3 configurations"""
        configs = config_manager.load_configs()
        
        # Verify S3 config
        assert "s3" in configs
        assert "BucketName" in configs["s3"]
        assert "Region" in configs["s3"]


class TestErrorHandling:
    """Integration tests for error handling"""
    
    def test_connection_error_handling(self, mock_load_configs):
        """Test error handling for database connection failures"""
        # Mock connection function to raise an exception
        with patch('utils.connect_db.connect_db', side_effect=Exception("Simulated connection error")):
            # Redirect stderr to capture error messages
            captured_error = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # This should handle the connection error gracefully
                connection_test.connection_test("postgresql")
                
                # No assertion needed - we just verify it doesn't raise an exception
            finally:
                sys.stderr = original_stderr
    
    def test_subprocess_error_handling(self, mock_load_configs, mock_postgres_connection, 
                                      monkeypatch, tmp_path):
        """Test error handling for subprocess failures during backup"""
        # Set up temporary directories
        temp_backup_dir = tmp_path / "backups"
        temp_backup_dir.mkdir(exist_ok=True)
        
        # Mock user input for "full" backup choice
        monkeypatch.setattr('builtins.input', lambda _: "full")
        
        # Mock subprocess.run to raise an exception
        mock_run = MagicMock(side_effect=subprocess.SubprocessError("Simulated subprocess error"))
        
        with patch('utils.connect_db.connect_db', return_value=mock_postgres_connection), \
             patch('subprocess.run', mock_run):
            
            # Redirect stderr to capture error messages
            captured_error = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # This should handle the subprocess error gracefully
                backup_database.backup("postgresql", str(temp_backup_dir), "local", 10)
                
                # No assertion needed - we just verify it doesn't raise an exception
            finally:
                sys.stderr = original_stderr
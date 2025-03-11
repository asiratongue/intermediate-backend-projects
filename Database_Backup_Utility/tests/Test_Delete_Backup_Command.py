import pytest
import os
import sys
import io
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile

# Import the delete_backup module
from src.commands.delete_backup import delete


class TestDeleteCommand:
    """Tests for the delete backup command"""
    
    def test_delete_db_backup_local(self, mock_load_configs, monkeypatch, tmp_path):
        """Test deleting local database backups"""
        # Create a temporary backup file
        backup_file = tmp_path / "test_backup.sql"
        backup_file.write_text("-- PostgreSQL dump")
        
        # Mock user inputs
        inputs = ["d", str(backup_file)]
        input_iter = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
        
        # Create a temporary backup list file
        backup_list_content = f"postgresql  {backup_file}\n"
        
        # Mock the open function to read the backup list
        mock_files = {
            str(Path(mock_load_configs["test_config_dir"], "db_backup_list.txt")): io.StringIO(backup_list_content)
        }
        
        def mock_open_func(file, *args, **kwargs):
            if file in mock_files and 'r' in args[0]:
                return mock_files[file]
            return mock_open()(file, *args, **kwargs)
        
        with patch('builtins.open', mock_open_func), \
             patch('os.remove') as mock_remove:
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the delete command
                delete()
                
                # Verify the correct operations were performed
                mock_remove.assert_called_with(str(backup_file))
                
                # Verify output
                output = captured_output.getvalue()
                assert f"{backup_file} sucessfully deleted" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_delete_table_backup_local(self, mock_load_configs, monkeypatch, tmp_path):
        """Test deleting local table backups"""
        # Create a temporary backup file
        backup_file = tmp_path / "test_users.csv"
        backup_file.write_text("id,name,email")
        
        # Mock user inputs
        inputs = ["t", str(backup_file)]
        input_iter = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
        
        # Create a temporary backup list file
        backup_list_content = f"postgresql  {backup_file}\n"
        
        # Mock the open function to read the backup list
        mock_files = {
            str(Path(mock_load_configs["test_config_dir"], "table_backup_list.txt")): io.StringIO(backup_list_content)
        }
        
        def mock_open_func(file, *args, **kwargs):
            if file in mock_files and 'r' in args[0]:
                return mock_files[file]
            return mock_open()(file, *args, **kwargs)
        
        with patch('builtins.open', mock_open_func), \
             patch('os.remove') as mock_remove:
            
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the delete command
                delete()
                
                # Verify the correct operations were performed
                mock_remove.assert_called_with(str(backup_file))
                
                # Verify output
                output = captured_output.getvalue()
                assert f"{backup_file} sucessfully deleted" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_delete_s3_backup(self, mock_load_configs, monkeypatch):
        """Test deleting S3 backups"""
        # S3 backup path
        s3_path = "s3://test-bucket/sql_backups/test_backup.sql.gz"
        
        # Mock user inputs
        inputs = ["d", s3_path]
        input_iter = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
        
        # Create a temporary backup list file
        backup_list_content = f"postgresql  {s3_path}\n"
        
        # Mock the open function to read the backup list
        mock_files = {
            str(Path(mock_load_configs["test_config_dir"], "db_backup_list.txt")): io.StringIO(backup_list_content)
        }
        
        def mock_open_func(file, *args, **kwargs):
            if file in mock_files and 'r' in args[0]:
                return mock_files[file]
            return mock_open()(file, *args, **kwargs)
        
        with patch('builtins.open', mock_open_func):
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the delete command
                delete()
                
                # Verify S3 delete_object was called
                assert mock_load_configs["s3"]["s3_client"].delete_object.called
                
                # Verify the correct parameters were used
                mock_load_configs["s3"]["s3_client"].delete_object.assert_called_with(
                    Bucket="test-bucket", 
                    Key="sql_backups/test_backup.sql.gz"
                )
                
                # Verify output
                output = captured_output.getvalue()
                assert f"{s3_path} sucessfully deleted" in output
            finally:
                sys.stdout = sys.__stdout__
    
    def test_invalid_choice(self, mock_load_configs, monkeypatch):
        """Test handling of invalid choice input"""
        # Mock user inputs - invalid choice first
        inputs = ["x", "d", ""]  # Invalid, then valid but no backups selected
        input_iter = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
        
        # Mock empty backup list
        with patch('builtins.open', mock_open(read_data="")):
            # Redirect stderr to capture error messages
            captured_error = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # This should handle the invalid input gracefully
                delete()
                
                # No assertion needed - we just verify it doesn't raise an exception
            finally:
                sys.stderr = original_stderr
    
    def test_no_backups_available(self, mock_load_configs, monkeypatch):
        """Test handling when no backups are available"""
        # Mock user input
        monkeypatch.setattr('builtins.input', lambda _: "d")
        
        # Mock empty backup list
        with patch('builtins.open', mock_open(read_data="")):
            # Capture stdout to verify output
            captured_output = io.StringIO()
            sys.stdout = captured_output
            
            try:
                # Execute the delete command
                delete()
                
                # Verify output
                output = captured_output.getvalue()
                assert "there are no backups currently available" in output.lower()
            finally:
                sys.stdout = sys.__stdout__
    
    def test_invalid_backup_path(self, mock_load_configs, monkeypatch):
        """Test handling of invalid backup path"""
        # Invalid backup path
        invalid_path = "/non/existent/backup.sql"
        
        # Mock user inputs
        inputs = ["d", invalid_path]
        input_iter = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
        
        # Create a temporary backup list file
        backup_list_content = f"postgresql  {invalid_path}\n"
        
        # Mock the open function to read the backup list
        mock_files = {
            str(Path(mock_load_configs["test_config_dir"], "db_backup_list.txt")): io.StringIO(backup_list_content)
        }
        
        def mock_open_func(file, *args, **kwargs):
            if file in mock_files and 'r' in args[0]:
                return mock_files[file]
            return mock_open()(file, *args, **kwargs)
        
        with patch('builtins.open', mock_open_func), \
             patch('os.remove', side_effect=FileNotFoundError):
            
            # Redirect stderr to capture error messages
            captured_error = io.StringIO()
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # This should handle the missing file gracefully
                delete()
                
                # No assertion needed - we just verify it doesn't raise an exception
            finally:
                sys.stderr = original_stderr
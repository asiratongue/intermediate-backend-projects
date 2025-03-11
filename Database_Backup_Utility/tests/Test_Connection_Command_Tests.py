import pytest
from unittest.mock import patch, MagicMock
import sys
import io
import os

# Import the test_connection module

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.commands.connection_test import connection_test


class TestConnectionCommand:
    """Tests for the test_connection command"""
    
    def test_postgresql_connection(self, mock_load_configs, mock_postgres_connection, capsys):
        """Test PostgreSQL connection command"""

        with patch('src.commands.connection_test.connect_db', return_value = mock_postgres_connection), \
             patch('src.commands.connection_test.configs', mock_load_configs):
            
            # Capture stdout to verify output
            connection_test("postgresql")
            captured = capsys.readouterr()
            
            # Verify the output contains the expected message
            expected_message = f"connection to {mock_load_configs['postgresql']['database']} is ok!"
            assert expected_message in captured.out

    def test_sqlite_connection(self, mock_load_configs, sqlite_db, capsys):
        """Test SQLite connection command"""
        with patch('src.utils.connect_db', return_value=sqlite_db), \
             patch('src.commands.connection_test.configs', mock_load_configs):
            # Capture stdout to verify output
            connection_test("sqlite")

            captured = capsys.readouterr()

            # Test the connection command
            connection_test("sqlite")
                
            # Verify the output contains the expected message
            expected_message = f"connection to {mock_load_configs['sqlite']['database']} is ok!"
            assert expected_message in captured.out

    
    def test_mongodb_connection(self, mock_load_configs, mock_mongodb_connection, capsys):
        """Test MongoDB connection command"""
        with patch('src.utils.connect_db', return_value=mock_mongodb_connection), \
            patch('src.commands.connection_test.configs', mock_load_configs):
            # Capture stdout to verify output
            connection_test("mongodb")
            captured = capsys.readouterr()
                       

            expected_message = f"connection to {mock_load_configs['mongodb']['database']} is ok!"
            assert expected_message in captured.out

    
    def test_unknown_db_type(self, mock_load_configs, capsys):
        """Test with an unknown database type"""
        # Capture stdout to verify output
        # Test with an unknown database type
        connection_test("unknown_db")

        captured = capsys.readouterr()
        
        # Verify the output contains the expected error message
        expected_message = "Unknown database type: unknown_db"
        assert expected_message in captured.out

    
    def test_connection_failure(self, mock_load_configs, capsys):
        """Test handling of connection failure"""
        # Mock connect_db to return None (connection failure)
        with patch('src.commands.connection_test.connect_db', return_value=None):

            # This should not print the success message
            connection_test("postgresql")

            captured = capsys.readouterr()
    
            success_message = f"connection to {mock_load_configs['postgresql']['database']} is ok!"
            assert success_message not in captured.out

#src.commands.connection_test.connect_db
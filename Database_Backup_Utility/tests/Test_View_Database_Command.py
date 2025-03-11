import pytest
from unittest.mock import patch, MagicMock
import sys
import io

# Import the view_database module
from src.commands.view_database import view


class TestViewCommand:
    """Tests for the view database command"""
    
    def test_view_sqlite(self, mock_load_configs, sqlite_db, capsys):
        """Test viewing SQLite database tables"""
        # Mock the cursor to return some table names
        cursor = MagicMock()
        cursor.fetchall.return_value = [('test_users',), ('test_products',)]
        
        # Mock the connection
        conn = MagicMock()
        conn.cursor.return_value = cursor
        
        with patch('src.commands.view_database.connect_db', return_value=conn), \
            patch('src.commands.view_database.configs', mock_load_configs):

                # Execute the view command
                view("sqlite")

                captured = capsys.readouterr()
                
                # Verify the correct SQL was executed
                cursor.execute.assert_called_with(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
                )
                
                # Verify the output contains the table names
                assert "table name:  test_users" in captured.out
                assert "table name:  test_products" in captured.out

    
    def test_view_postgresql(self, mock_load_configs, mock_postgres_connection, capsys):
        """Test viewing PostgreSQL database tables"""
        # Mock the cursor
        cursor = mock_postgres_connection.cursor()
        cursor.fetchall.return_value = [('test_users',), ('test_products',)]
        
        with patch('src.commands.view_database.connect_db', return_value=mock_postgres_connection), \
            patch('src.commands.view_database.configs', mock_load_configs):
            # Capture stdout to verify output
            view("postgresql")
            
            captured = capsys.readouterr()

            # Verify the correct SQL was executed
            cursor.execute.assert_called_with(
                "SELECT relname FROM pg_class WHERE relkind='r' AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')"
            )
            
            assert "table name:  test_users" in captured.out
            assert "table name:  test_products" in captured.out

    
    def test_view_mongodb(self, mock_load_configs, mock_mongodb_connection, capsys):
        """Test viewing MongoDB collections"""
        # Mock the database
        client, db = mock_mongodb_connection
        db.list_collection_names.return_value = ['test_users', 'test_products']
        
        with patch('src.commands.view_database.connect_db', return_value=mock_mongodb_connection), \
            patch('src.commands.view_database.configs', mock_load_configs):
            # Capture stdout to verify output

            # Execute the view command
            view("mongodb")
            
            # Verify the output contains the collection names
            captured = capsys.readouterr()
            assert "collection name:  test_users" in captured.out
            assert "collection name:  test_products" in captured.out

    
    def test_view_unknown_db(self, mock_load_configs):
        """Test view command with unknown database type"""
        # Capture stdout to verify output and stderr for error messages
        captured_output = io.StringIO()
        captured_error = io.StringIO()
        sys.stdout = captured_output
        original_stderr = sys.stderr
        sys.stderr = captured_error
        
        try:
            # Execute the view command with an unknown database type
            view("unknown_db")
            
            # Verify no output is generated
            output = captured_output.getvalue()
            assert output == ""
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = original_stderr
    
    def test_view_no_tables(self, mock_load_configs):
        """Test view command when no tables are found"""
        # Mock the connection and cursor
        cursor = MagicMock()
        cursor.fetchall.return_value = []
        
        conn = MagicMock()
        conn.cursor.return_value = cursor
        
        with patch('utils.connect_db.connect_db', return_value=conn):
            # Capture stdout to verify output and stderr for error messages
            captured_output = io.StringIO()
            captured_error = io.StringIO()
            sys.stdout = captured_output
            original_stderr = sys.stderr
            sys.stderr = captured_error
            
            try:
                # Execute the view command
                view("sqlite")
                
                # Verify no table output is generated
                output = captured_output.getvalue()
                assert "table name:" not in output
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = original_stderr
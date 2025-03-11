import os
import sys
import pytest
import json
import sqlite3
import tempfile
import shutil
from pathlib import Path
import psycopg2
import pymongo
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Import application modules
from src.config import config_manager
from src.utils.connect_db import connect_db
from src.utils.logger_setup import logger

# Paths for test resources
TEST_DIR = Path(__file__).parent
TEST_RESOURCES_DIR = TEST_DIR / "tests" / "resources"
TEST_CONFIG_DIR = TEST_RESOURCES_DIR / "config"
TEST_BACKUP_DIR = TEST_RESOURCES_DIR / "backups"
TEST_TEMP_DIR = TEST_RESOURCES_DIR / "temp"

# Ensure required directories exist
for directory in [TEST_RESOURCES_DIR, TEST_CONFIG_DIR, TEST_BACKUP_DIR, TEST_TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Test database configurations
TEST_SQLITE_DB = TEST_RESOURCES_DIR / "test_db.sqlite3"
TEST_POSTGRES_DB = "test_backup_db"
TEST_MONGO_DB = "test_backup_db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Set up the test environment with test configurations and clean temp directories.
    This fixture runs once at the beginning of the test session.
    """
    # Create test configuration files
    create_test_configs()
    
    # Clean any existing files in temp directory
    for file in TEST_TEMP_DIR.glob("*"):
        if file.is_file():
            file.unlink()
        elif file.is_dir():
            shutil.rmtree(file)
    
    # Create backup list files if they don't exist
    for filename in ["db_backup_list.txt", "table_backup_list.txt"]:
        backup_list_file = TEST_CONFIG_DIR / filename
        if not backup_list_file.exists():
            with open(backup_list_file, "w") as f:
                pass
    
    # Patch the backup_list_path in various modules
    modules_to_patch = [
        "src.commands.backup_database",
        "src.commands.delete_backup",
        "src.commands.restore_database",
        "src.config.config_manager"
    ]
    
    patchers = []
    for module in modules_to_patch:
        patcher = patch(f"{module}.backup_list_path", TEST_CONFIG_DIR)
        patchers.append(patcher)
        patcher.start()
    
    # Let tests run
    yield
    
    # Stop all patchers
    for patcher in patchers:
        patcher.stop()
    
    # Clean up
    cleanup_test_environment()

def create_test_configs():
    """Create test configuration files"""
    # PostgreSQL config
    postgres_config = {
        "host": "localhost",
        "port": "5432",
        "database": TEST_POSTGRES_DB,
        "user": "postgres",
        "password": "postgres",  # Use a test password
        "Local": True,
        "type": "postgresql"
    }
    
    # MongoDB config
    mongo_config = {
        "protocol": "mongodb://",
        "host": "localhost:27017",
        "user": "",
        "password": "",
        "Local": True,
        "type": "mongodb",
        "database": TEST_MONGO_DB,
        "connection_string": "mongodb://localhost:27017"
    }
    
    # S3 config
    s3_config = {
        "BucketName": "test-bucket",
        "Region": "us-east-1",
        "AccessControl": "Private",
        "Versioning": False,
        "Encryption": True
    }
    
    # Write configs to files
    with open(TEST_CONFIG_DIR / "config_postgresql.json", "w") as f:
        json.dump(postgres_config, f, indent=2)
    
    with open(TEST_CONFIG_DIR / "config_mongodb.json", "w") as f:
        json.dump(mongo_config, f, indent=2)
    
    with open(TEST_CONFIG_DIR / "s3_config.json", "w") as f:
        json.dump(s3_config, f, indent=2)

def cleanup_test_environment():
    """Clean up the test environment"""
    # Clean any temporary database files
    if TEST_SQLITE_DB.exists():
        TEST_SQLITE_DB.unlink()
    
    # Clean backup lists
    for filename in ["db_backup_list.txt", "table_backup_list.txt"]:
        backup_list_file = TEST_CONFIG_DIR / filename
        if backup_list_file.exists():
            with open(backup_list_file, "w") as f:
                pass

@pytest.fixture
def mock_load_configs():
    """Mock the config_manager.load_configs function to return test configurations"""
    with patch("config.config_manager.load_configs") as mock_load:
        # Create mock configurations
        mock_configs = {
            "postgresql": {
                "host": "localhost",
                "port": "5432",
                "database": TEST_POSTGRES_DB,
                "user": "postgres",
                "password": "postgres",
                "Local": True,
                "type": "postgresql"
            },
            "sqlite": {
                "type": "sqlite",
                "path": str(TEST_SQLITE_DB),
                "database": "test_database"
            },
            "mongodb": {
                "protocol": "mongodb://",
                "host": "localhost:27017",
                "user": "",
                "password": "",
                "Local": True,
                "type": "mongodb",
                "database": TEST_MONGO_DB,
                "connection_string": "mongodb://localhost:27017"
            },
            "s3": {
                "BucketName": "test-bucket",
                "Region": "us-east-1",
                "AccessControl": "Private",
                "Versioning": False,
                "Encryption": True,
                "s3": MagicMock(),
                "s3_client": MagicMock(),
                "bucket": MagicMock()
            },

            "test_config_dir" : TEST_CONFIG_DIR
        }
        
        # Configure mock S3 client
        mock_configs["s3"]["s3_client"].delete_object = MagicMock()
        
        mock_load.return_value = mock_configs
        yield mock_configs

@pytest.fixture
def sqlite_db():
    """Create and populate a test SQLite database"""
    # Create a new SQLite database file
    conn = sqlite3.connect(TEST_SQLITE_DB)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT
        )
    ''')
    
    # Insert test data
    users = [
        (1, 'John Doe', 'john@example.com', '2023-01-01'),
        (2, 'Jane Smith', 'jane@example.com', '2023-01-02'),
        (3, 'Bob Johnson', 'bob@example.com', '2023-01-03')
    ]
    
    products = [
        (1, 'Laptop', 1299.99, 'Electronics'),
        (2, 'Headphones', 149.99, 'Electronics'),
        (3, 'Desk Chair', 249.99, 'Furniture')
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO test_users VALUES (?, ?, ?, ?)', users)
    cursor.executemany('INSERT OR REPLACE INTO test_products VALUES (?, ?, ?, ?)', products)
    
    conn.commit()
    
    yield conn
    
    # Cleanup
    conn.close()

@pytest.fixture
def mock_postgres_connection():
    """Mock a PostgreSQL connection"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Configure the mock cursor to return appropriate data
    mock_cursor.fetchall.return_value = [
        ('test_users',),
        ('test_products',)
    ]
    
    # For table column info
    def execute_side_effect(query, *args, **kwargs):
        if "information_schema.columns" in query:
            mock_cursor.fetchall.return_value = [
                ('id', 'integer'),
                ('name', 'text'),
                ('email', 'text'),
                ('created_at', 'timestamp')
            ]
        elif "pg_class" in query:
            mock_cursor.fetchall.return_value = [
                ('test_users',),
                ('test_products',)
            ]
    
    mock_cursor.execute.side_effect = execute_side_effect
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock connection info
    mock_conn.info = MagicMock()
    mock_conn.info.dbname = TEST_POSTGRES_DB
    mock_conn.info.user = "postgres"
    
    with patch('psycopg2.connect', return_value=mock_conn):
        yield mock_conn

@pytest.fixture
def mock_mongodb_connection():
    """Mock a MongoDB connection"""
    mock_client = MagicMock()
    mock_db = MagicMock()
    
    # Configure the mock database
    mock_db.list_collection_names.return_value = ['test_users', 'test_products']
    mock_client.__getitem__.return_value = mock_db
    
    with patch('pymongo.MongoClient', return_value=mock_client):
        yield (mock_client, mock_db)

@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="", stdout="")
        yield mock_run

@pytest.fixture
def mock_input(monkeypatch):
    """Mock user input with predefined responses"""
    inputs = iter(['full', 'Y', 'test_users', 'Y'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    return inputs

@pytest.fixture
def temp_backup_dir():
    """Create a temporary backup directory"""
    backup_dir = tempfile.mkdtemp(dir=TEST_TEMP_DIR)
    dump_dir = os.path.join(backup_dir, "dump_exports")
    csv_dir = os.path.join(backup_dir, "csv_exports")
    
    os.makedirs(dump_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    
    yield backup_dir
    
    # Cleanup is handled by the setup_test_environment fixture
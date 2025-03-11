#!/usr/bin/env python
"""
Test Database Seeder Script
---------------------------
This script creates and populates test databases for the DBMS Utility tests.
It should be run before executing the test suite to ensure proper test data.

Supported databases:
- SQLite (local file)
- PostgreSQL (requires local PostgreSQL server)
- MongoDB (requires local MongoDB server)

Usage:
    python setup_test_databases.py

Requirements:
    - psycopg2-binary
    - pymongo
    - sqlite3 (built-in)
"""

import os
import sys
import sqlite3
import psycopg2
import pymongo
import json
from pathlib import Path
import argparse

# Constants
TEST_DIR = Path(__file__).parent
TEST_RESOURCES_DIR = TEST_DIR / "test_docs" / "resources"
TEST_CONFIG_DIR = TEST_RESOURCES_DIR / "config"
TEST_BACKUP_DIR = TEST_RESOURCES_DIR / "backups"
TEST_TEMP_DIR = TEST_RESOURCES_DIR / "temp"

# Test database configurations
TEST_SQLITE_DB = TEST_RESOURCES_DIR / "test_db.sqlite3"
TEST_POSTGRES_DB = "test_postgres_db"
TEST_MONGO_DB = "test_mongo_db"

# Ensure required directories exist
for directory in [TEST_RESOURCES_DIR, TEST_CONFIG_DIR, TEST_BACKUP_DIR, TEST_TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def setup_sqlite():
    """Create and populate a test SQLite database"""
    print(f"Setting up SQLite test database at {TEST_SQLITE_DB}...")
    
    # Remove existing database if it exists
    if TEST_SQLITE_DB.exists():
        TEST_SQLITE_DB.unlink()
    
    # Create a new SQLite database
    conn = sqlite3.connect(TEST_SQLITE_DB)
    cursor = conn.cursor()
    
    # Create test tables
    cursor.execute('''
        CREATE TABLE test_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE test_products (
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
    
    cursor.executemany('INSERT INTO test_users VALUES (?, ?, ?, ?)', users)
    cursor.executemany('INSERT INTO test_products VALUES (?, ?, ?, ?)', products)
    
    conn.commit()
    conn.close()
    
    print("SQLite test database setup complete.")


def setup_postgresql():
    """Create and populate a test PostgreSQL database"""
    print(f"Setting up PostgreSQL test database '{TEST_POSTGRES_DB}'...")
    
    # PostgreSQL connection parameters
    postgres_params = {
        "host": "localhost",
        "port": "5432",
        "database": "postgres",  # Connect to default database first
        "user": "postgres",
        "password": "password"
    }
    
    try:
        # Connect to the default PostgreSQL database
        conn = psycopg2.connect(**postgres_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_POSTGRES_DB}'")
        exists = cursor.fetchone()
        
        # Drop the database if it exists
        if exists:
            cursor.execute(f"DROP DATABASE {TEST_POSTGRES_DB}")
        
        # Create a new test database
        cursor.execute(f"CREATE DATABASE {TEST_POSTGRES_DB}")
        
        # Close the connection to the default database
        cursor.close()
        conn.close()
        
        # Connect to the new test database
        postgres_params["database"] = TEST_POSTGRES_DB
        conn = psycopg2.connect(**postgres_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create test tables
        cursor.execute('''
            CREATE TABLE test_users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE test_products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
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
        
        cursor.executemany('INSERT INTO test_users (id, name, email, created_at) VALUES (%s, %s, %s, %s)', users)
        cursor.executemany('INSERT INTO test_products (id, name, price, category) VALUES (%s, %s, %s, %s)', products)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("PostgreSQL test database setup complete.")
    
    except psycopg2.Error as e:
        print(f"Error setting up PostgreSQL test database: {e}")
        return False
    
    return True


def setup_mongodb():
    """Create and populate a test MongoDB database"""
    print(f"Setting up MongoDB test database '{TEST_MONGO_DB}'...")
    
    try:
        # Connect to MongoDB with a timeout
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        
        # Force a connection to verify the server is available
        client.admin.command('ping')
        
        # Drop the test database if it exists
        client.drop_database(TEST_MONGO_DB)
        
        # Create a new test database
        db = client[TEST_MONGO_DB]
        
        # Create test collections and insert data
        users = [
            {
                "_id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "created_at": "2023-01-01",
                "profile": {
                    "age": 30,
                    "location": "New York"
                }
            },
            {
                "_id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "created_at": "2023-01-02",
                "profile": {
                    "age": 28,
                    "location": "San Francisco"
                }
            },
            {
                "_id": 3,
                "name": "Bob Johnson",
                "email": "bob@example.com",
                "created_at": "2023-01-03",
                "profile": {
                    "age": 35,
                    "location": "Chicago"
                }
            }
        ]
        
        products = [
            {
                "_id": 1,
                "name": "Laptop",
                "price": 1299.99,
                "category": "Electronics",
                "specs": {
                    "processor": "Intel i7",
                    "memory": "16GB",
                    "storage": "512GB SSD"
                }
            },
            {
                "_id": 2,
                "name": "Headphones",
                "price": 149.99,
                "category": "Electronics",
                "specs": {
                    "type": "Over-ear",
                    "wireless": True,
                    "battery_life": "30 hours"
                }
            },
            {
                "_id": 3,
                "name": "Desk Chair",
                "price": 249.99,
                "category": "Furniture",
                "specs": {
                    "material": "Mesh",
                    "adjustable": True,
                    "color": "Black"
                }
            }
        ]
        
        # Insert data into collections
        db.test_users.insert_many(users)
        db.test_products.insert_many(products)
        
        print("MongoDB test database setup complete.")
        return True
    
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Is MongoDB running on localhost:27017?")
        return False
    except Exception as e:
        print(f"Error setting up MongoDB test database: {e}")
        return False
    

def create_test_configs():
    """Create test configuration files"""
    print("Creating test configuration files...")
    
    # PostgreSQL config
    postgres_config = {
        "host": "localhost",
        "port": "5432",
        "database": TEST_POSTGRES_DB,
        "user": "postgres",
        "password": "postgres",
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
    
    # SQLite config
    sqlite_config = {
        "type": "sqlite",
        "path": str(TEST_SQLITE_DB),
        "database": "test_database"
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
    
    with open(TEST_CONFIG_DIR / "config_sqlite.json", "w") as f:
        json.dump(sqlite_config, f, indent=2)
    
    with open(TEST_CONFIG_DIR / "s3_config.json", "w") as f:
        json.dump(s3_config, f, indent=2)
    
    # Create backup list files
    for filename in ["db_backup_list.txt", "table_backup_list.txt"]:
        backup_list_file = TEST_CONFIG_DIR / filename
        if not backup_list_file.exists():
            with open(backup_list_file, "w") as f:
                pass
    
    print("Test configuration files created.")


def main():
    """Main function to set up test databases and configurations"""
    parser = argparse.ArgumentParser(description="Set up test databases for DBMS Utility tests")
    parser.add_argument("--sqlite", action="store_true", help="Set up SQLite test database only")
    parser.add_argument("--postgres", action="store_true", help="Set up PostgreSQL test database only")
    parser.add_argument("--mongodb", action="store_true", help="Set up MongoDB test database only")
    parser.add_argument("--configs", action="store_true", help="Create test configurations only")
    parser.add_argument("--all", action="store_true", help="Set up all test databases and configurations")
    parser.add_argument("--skip-mongo", action="store_true", help="Skip MongoDB setup")

    args = parser.parse_args()
    
    # If no specific arguments are provided, set up everything
    if not any([args.sqlite, args.postgres, args.mongodb, args.configs, args.all]):
        args.all = True
    
    # Create test directories
    for directory in [TEST_RESOURCES_DIR, TEST_CONFIG_DIR, TEST_BACKUP_DIR, TEST_TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Set up databases and configurations based on arguments
    if args.all or args.configs:
        create_test_configs()
    
    if args.all or args.sqlite:
        setup_sqlite()
    
    if args.all or args.postgres:
        setup_postgresql()
    
    if (args.all or args.mongodb) and not args.skip_mongo:
        mongo_success = setup_mongodb()
    elif args.skip_mongo:
        print("Skipping MongoDB setup as requested.")
        mongo_success = True
    
    print("Test environment setup complete.")


if __name__ == "__main__":
    main()

    
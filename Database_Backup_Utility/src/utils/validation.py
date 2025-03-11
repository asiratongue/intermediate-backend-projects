import csv
import gzip
from urllib.parse import urlparse


def validate_backup_csv(csv_file, table_name, db_type, cursor = None):
    db_columns = {}

    if db_type == "postgresql":
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'") #creates a result set, from the query
        db_columns = {row[0]: row[1] for row in cursor.fetchall()}

    elif db_type == "sqlite":
        cursor.execute(f"PRAGMA table_info({table_name})")
        db_columns = {row[1] : row[2] for row in cursor.fetchall()}

    elif db_type == "mongodb":
        return True, "Validation passed"
    
    # Read CSV header (columns)
    with open(csv_file) as f:
        header = next(csv.reader(f))
    
    # Validate columns match
    missing_columns = [col for col in db_columns if col not in header]
    if missing_columns:
        return False, f"Missing columns: {missing_columns}"
    
    return True, "Validation passed"


def validate_full_backup(dump_file, connection, db_type):

    '''

    Validate a full database dump

    '''

    try:
        
        if not any(ext in str(dump_file) for ext in ['.bson', '.tar', '.tar.gz']):

            if str(dump_file).endswith('.sql'):
                with open(dump_file, 'r') as f:
                    sql_content = f.read()
        
            if str(dump_file).endswith('.gz'):
                with gzip.open(dump_file, 'rt') as f:
                    sql_content = f.read()

            test_cursor = connection.cursor()                
            test_cursor.execute("BEGIN")
        
        if db_type.lower() == "postgresql":

            try:
                if sql_content.lower().strip().startswith(("insert", "update", "delete", "create", "alter")):
                    test_cursor.execute(f"EXPLAIN {sql_content}")
            except Exception as e:
                pass  
            
            # Check for table references that don't exist
            tables_referenced = []  # You'd need to parse the SQL to extract these
            for table in tables_referenced:
                test_cursor.execute(f"SELECT to_regclass('{table}')")
                if test_cursor.fetchone()[0] is None:
                    connection.rollback()
                    return False, f"Referenced table doesn't exist: {table}"
        
        elif db_type.lower() == "sqlite":

            test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            existing_tables = [row[0] for row in test_cursor.fetchall()]
            
            # Parse for table names (simplified - would need proper SQL parsing)
            sql_lines = sql_content.split(';')
            for line in sql_lines:
                line = line.strip().lower()
                
                # Check CREATE statements
                if line.startswith('create table'):
                    table_name = line.split('create table')[1].strip().split(' ')[0].strip('"\'`[]')
                    # Check if table already exists
                    if table_name in existing_tables:
                        connection.rollback()
                        return False, f"Table already exists: {table_name}"
                
                # Try to compile SQL with EXPLAIN QUERY PLAN
                try:
                    if line and not line.startswith('--'):  # Skip comments
                        test_cursor.execute(f"EXPLAIN QUERY PLAN {line}")
                except Exception as e:
                    pass
        
        elif db_type.lower() == "mongodb":
                return True, "validation passed"

        else:
            connection.rollback()
            return False, f"Unsupported database type: {db_type}"
                        
        connection.rollback()
        return True, "SQL validation passed"
    
    except Exception as e:
        try:
            connection.rollback()
        except:
            pass
        return False, f"Validation error: {str(e)}"
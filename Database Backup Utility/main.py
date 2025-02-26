import logging
import psycopg2
import psycopg2.extras
import typer
import json
import subprocess
from pathlib import Path
import os
import boto3
from botocore.config import Config
from psycopg2 import sql

app = typer.Typer()

with open('config_postgresql.json', 'r') as file:
    file.seek(0, 2)  
    if file.tell() > 0:  
        file.seek(0)  
        sql_data = json.load(file)


with open('s3_config.json', 'r') as file:
    file.seek(0, 2)  
    if file.tell() > 0:  
        file.seek(0)  
        s3_config = json.load(file)

        aws_config = Config(region_name = s3_config["Region"], 
                            signature_version = 'v4',
                            retries = {'max_attempts': 10, 'mode': 'standard'
                        })

        s3 = boto3.resource('s3', config=aws_config)
        bucket = s3.Bucket(s3_config["BucketName"])


def connect_db(sql_data):

    try:
        conn = psycopg2.connect(
        host=sql_data["host"],
        port=sql_data["port"],
        database=sql_data["database"],
        user=sql_data["user"],
        password=sql_data["password"]
    )

        return(conn)
    
    except psycopg2.OperationalError as e:
            print(f"Error: Unable to connect to the database. Details : {e}")


@app.command()
def test_connection():
    connect_db(sql_data)
    print(f"connection to {sql_data["database"]} is ok!")


def connect_as_superuser():  #lower the permission level.
    import getpass
    postgres_password = getpass.getpass("Postgres superuser password: ")
    
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="mydevelopmentdb",
        user="postgres",
        password=postgres_password
    )
    return conn

@app.command()
def view(db: str):

    if db == "postgres":

        conn = connect_db(sql_data)
        
        cur = conn.cursor()
        cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')")
        print(f"Connected to database: {conn.info.dbname} as user: {conn.info.user}")

        tables = cur.fetchall()

        if not tables:
            print("no tables found in schema!")
            return
        
        for table in tables:
            print("table name: ", table[0])
            

        cur.close()
        conn.close()

@app.command()
def backup(db_type, 
           backup_path, 
           storage: str = typer.Argument(None, help="type cloud, in order to back up with chosen cloud service, will save locally first.")
           ):

    user_input = input("please list the table names you want backed up, else type 'full' in order to create a full db dump: ")  #make input validation more robust
    user_input = user_input.strip()

    #full .sql db dump
    if user_input.lower() == 'full':

        suffix_name =  f"{sql_data["database"]}_dump.sql"
        sql_dump_path = Path(f"{backup_path}/{suffix_name}")
        loc = sql_dump_path    
        if db_type == "postgres":  

            try:
                if sql_data["Local"] == False:
                    subprocess.run(['pg_dump', '-h', f'{sql_data["host"]}','-p', sql_data["port"],'-U', sql_data["user"],'-d', sql_data["database"],'--data-only',
                    '--no-owner','--no-privileges','-f', f'{sql_dump_path}'])

                else:
                    superuser_conn = connect_as_superuser()
                    superuser_cursor = superuser_conn.cursor()
                    superuser_cursor.execute(f"ALTER USER {sql_data["user"]} WITH SUPERUSER")
                    superuser_conn.commit() 

                    subprocess.run(['pg_dump', '-h', f'{sql_data["host"]}', '-p', sql_data["port"], '-U', sql_data["user"], '-d', sql_data["database"], '-f', f'{sql_dump_path}'])

                if storage == 'cloud':
                    subprocess.run(['aws', 's3', 'cp', f'{sql_dump_path}', f's3://{s3_config["BucketName"]}/sql_backups/{suffix_name}'])
                    loc = f's3://{s3_config["BucketName"]}/sql_backups/{suffix_name}'

            finally:
                if sql_data["Local"] != False:
                    superuser_cursor.execute(f"ALTER USER {sql_data["user"]} WITH NOSUPERUSER")
                    superuser_conn.commit()
                    superuser_cursor.close()
                    superuser_conn.close()

            print(f"Successfully backed up {sql_data["database"]} to {loc}")

    #partial .csv dump
    else: 
        if db_type == "postgres":
                
                try:
                    connection = connect_db(sql_data)
                    cursor = connection.cursor()
                    table_list = user_input.split()

                    csv_dir = os.path.join(backup_path, "csv_exports")
                    loc = csv_dir
                    os.makedirs(csv_dir, exist_ok=True)

                    for table in table_list:
                        print(table)
 
                        try:
                            csv_file_path = os.path.join(csv_dir, f"{table}.csv")
                            with open(csv_file_path, 'w') as file:
                                cursor.copy_expert(sql.SQL("COPY {} TO STDOUT WITH CSV HEADER").format(sql.Identifier("public", table)), file)                                
                            print(f"Exported {table} to CSV")

                            if storage == 'cloud':
                                subprocess.run(['aws', 's3', 'cp', f'{csv_file_path}', f's3://{s3_config["BucketName"]}/csv_exports/{table}.csv'])
                                loc = f's3://{s3_config["BucketName"]}/csv_exports/'

                        except Exception as e:
                            print(f"error backing up {table} : {e}")
                finally:
                    cursor.close()
                    connection.close()
                    
                         
                print(f"successfully backed up {len(table_list)} tables to {loc}")

if __name__ == "__main__":
    app()


#python main.py backup postgres G:\01101000111101\Programming\Projects\intermediate-backend-projects

#python main.py backup postgres G:\01101000111101\Programming\Projects\intermediate-backend-projects cloud

#python main.py view postgres



# table name:  users
# table name:  user_game_profiles
# table name:  games
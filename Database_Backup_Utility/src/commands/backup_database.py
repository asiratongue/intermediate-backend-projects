import subprocess
from datetime import datetime
from utils.connect_db import connect_db
from config import config_manager
from utils.logger_setup import logger
import os
import shutil
import sqlite3
import gzip
from psycopg2 import sql, errors
from pathlib import Path
import tarfile
from utils import validation
import csv
import json


def formatted_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

configs = config_manager.load_configs()
backup_list_path = Path(r"G:\01101000111101\Programming\Projects\intermediate-backend-projects\Database_Backup_Utility\src\config")

"""BACKUP DATABASE/TABLES COMMAND"""
def backup(db_type : str, backup_path : str, storage: str, compression: int):

    db_connection = connect_db(configs[db_type])
    timestamp_string = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    user_input = input("please list the table names you want backed up, else type 'full' in order to create a full db dump: ") 

    if not isinstance(user_input, str):
        logger.error("Invalid input, you must type 'full', or your table/collection names to back up!")
        return
    
    if compression > 10 or compression < 1 :
        logger.error("Compression values must be between 1 and 10!")
        return 
    
    user_input = user_input.strip()

    #full .sql db dump
    if user_input.lower() == 'full':

        dump_dir = os.path.join(backup_path, "dump_exports")
        os.makedirs(dump_dir, exist_ok=True)
        
        sql_suffix =  f"{timestamp_string}_{configs[db_type]["database"]}_dump.sql"
        mongo_suffix = f"{timestamp_string}_{configs[db_type]["database"]}_dump.tar"
        path_dict = {"mongodb" : Path(f"{dump_dir}/{mongo_suffix}"), "postgresql" : Path(f"{dump_dir}/{sql_suffix}"), "sqlite" : Path(f"{dump_dir}/{sql_suffix}")}

        def subprocess_creation(db_data, compression, db_dump_path, db_type):
                
                logger.info(f"starting subprocess creation @ {formatted_timestamp()}")
                temp_file = f"{db_dump_path}.temp"

                if db_type == 'sqlite':
                    db_path = str(db_data["path"])
                    subprocess_list = ['sqlite3', db_path, '.dump']

                elif db_type == 'postgresql':                   
                    subprocess_list = ['pg_dump', '-h', f'{db_data["host"]}', '-p', db_data["port"], '-U', db_data["user"], '-d', db_data["database"]]

                    if not db_data["Local"]:
                        subprocess_list.extend(['--no-owner','--no-privileges'])

                elif db_type == 'mongodb':
                    uri_string = '--uri=' + configs["mongodb"]["connection_string"] + f'/{configs["mongodb"]["database"]}'
                    dump_str_path = db_dump_path.with_suffix('')
                    output_file = f"{path_dict['mongodb']}"
                    logger.info(f"running subprocess for {db_type}")        
                    subprocess.run(['mongodump', uri_string, f'--out={dump_str_path}'])
                    subprocess_list = ["echo"]

                    if compression != 10:     
                        output_file = output_file + '.gz'
                        with tarfile.open(output_file, "w:gz", compresslevel=compression) as tar:
                            tar.add(dump_str_path, arcname=os.path.basename(db_dump_path))

                    else:                                         
                        with tarfile.open(output_file, "w") as tar:
                            tar.add(dump_str_path, arcname=os.path.basename(db_dump_path))

                if db_type in ['postgresql', 'sqlite']:
                    output_file = path_dict[db_type] if compression == 10 else f"{path_dict[db_type]}.gz"

                    logger.info(f"running subprocess for {db_type} with arguments: {subprocess_list}")
                    subprocess.run(subprocess_list, stdout=open(temp_file, 'w'))
                    
                    with open(temp_file, 'r') as infile:

                        if compression == 10:
                            with open(output_file, 'w') as outfile:
                                for line in infile:
                                    if 'transaction_timeout' not in line:
                                        outfile.write(line)
                
                        else:
                            with gzip.open(output_file, 'wt', compresslevel=compression) as outfile:
                                for line in infile:
                                    if 'transaction_timeout' not in line:
                                        outfile.write(line)

                if db_type == 'mongodb':
                    shutil.rmtree(dump_str_path)
                else:
                    os.remove(temp_file)

                logger.info(f"finished subprocess creation @ {formatted_timestamp()}")
                return subprocess_list, output_file

        try:
            
            if db_type == 'postgresql' and configs['postgresql']["Local"] == True:
                superuser_cursor = db_connection.cursor()
                superuser_cursor.execute(f"ALTER USER {configs['postgresql']["user"]} WITH SUPERUSER")
                db_connection.commit() 

            subprocess_command = subprocess_creation(db_data = configs[db_type], compression = compression, db_dump_path=path_dict[db_type], db_type=db_type)
            loc = subprocess_command[1]

            if storage == 'cloud':
                name = os.path.basename(loc)
                subprocess.run(['aws', 's3', 'cp', loc, f's3://{configs["s3"]["BucketName"]}/sql_backups/{name}']) ##
                loc = f's3://{configs["s3"]["BucketName"]}/sql_backups/{name}'

        finally:
            if db_type == 'postgresql' and configs['postgresql']["Local"] != False:
                superuser_cursor.execute(f"ALTER USER {configs['postgresql']["user"]} WITH NOSUPERUSER")
                db_connection.commit()
                db_connection.close()
                superuser_cursor.close()

        with open(Path(backup_list_path, 'db_backup_list.txt'), 'a+') as f:
            f.write(f'{db_type}  {loc}\n')
            
        valid_chk_sql = validation.validate_full_backup(dump_file=subprocess_command[1] , connection=connect_db(configs[db_type]), db_type=db_type) 

        if valid_chk_sql[0]:
            print(valid_chk_sql[1])
            print(f"Successfully backed up {configs[db_type]["database"]} to {loc}")

        else:
            logger.error(f"Validate function returned : {valid_chk_sql[0]}")
            logger.error(f"{valid_chk_sql[1]} ")


    #partial .csv dump
    else: 
        table_list = user_input.split()
        csv_dir = os.path.join(backup_path, "csv_exports")
        os.makedirs(csv_dir, exist_ok=True)

        try:
            if db_type in ['postgresql', 'sqlite']:
                cursor = db_connection.cursor()

            for table in table_list:
                try:
                    csv_file_path = os.path.join(csv_dir, f"{timestamp_string}_{table}.csv")
                    loc = csv_file_path
                    with open(csv_file_path, 'w') as file:

                        if db_type == "postgresql":
                            try:
                                cursor.copy_expert(sql.SQL("COPY {} TO STDOUT WITH CSV HEADER").format(sql.Identifier("public", table)), file)
                            except errors.UndefinedTable as e:
                                logger.error(f"The table '{table}' doesn't exist in the database.")

                        elif db_type == 'sqlite':
                            try:
                                cursor.execute(f"SELECT * FROM {table}")
                            except sqlite3.OperationalError as e:
                                logger.error(f"The table '{table}' doesn't exist in the database.")

                            rows = cursor.fetchall()
                            columns = [desc[0] for desc in cursor.description]
                            writer = csv.writer(file)
                            writer.writerow(columns)
                            writer.writerows(rows)

                        elif db_type == 'mongodb':
                            output_json = os.path.join (csv_dir, f"{timestamp_string}_{table}.json")
                            export_uri = f"{configs["mongodb"]}/{configs["mongodb"]["database"]}"
                            print("Export uri :", export_uri)
                            subprocess.run(["mongoexport", f"--uri={export_uri}", f"--collection={table}", f"--out={output_json}"])

                            with open (output_json, 'r') as json_file:
                                data = [json.loads(line) for line in json_file]

                                if data:
                                    headers = data[0].keys()

                                    writer = csv.DictWriter(file, fieldnames=headers)
                                    writer.writeheader() #creates the CSV header row using keys from the first MONGODB doc,
                                    writer.writerows(data) #writes all documents as rows in the CSV file.
                                    json_file.close()
                                    os.remove(output_json)
                                    file.close()

                    if db_type in ['postgresql', 'sqlite']:
                        csv_check = validation.validate_backup_csv(csv_file=csv_file_path, table_name=table, db_type=db_type , cursor=cursor)

                        if not csv_check[0]:
                            logger.error(f"error : {csv_check[1]}")
                            return

                    print(f"Converted {table} to {csv_file_path}")

                    if compression < 10:
                        with open(csv_file_path, 'rb') as f_in:
                            with gzip.open(csv_file_path + '.gz', 'wb', compresslevel=compression) as f_out:
                                f_out.write(f_in.read())
                                loc = csv_file_path+'.gz'

                        os.remove(csv_file_path)
                        
                    if storage == 'cloud':
                        subprocess.run(['aws', 's3', 'cp', f'{csv_file_path}', f's3://{configs['s3']["BucketName"]}/csv_exports/{table}.csv'])
                        loc = f's3://{configs['s3']["BucketName"]}/csv_exports/{table}.csv'

                    with open(Path(backup_list_path, 'table_backup_list.txt'), 'a+') as f:
                            f.write(f'{db_type}   {loc}\n') 
                 
                    print(f"successfully backed up {table} to {loc}")

                except Exception as e:
                    logger.error(f"error backing up {table} : {e}")

        finally:
            print(f"backed up {len(table_list)} tables")
            if db_type == 'postgresql' or db_type == 'sqlite':
                cursor.close()
                db_connection.close()

        return
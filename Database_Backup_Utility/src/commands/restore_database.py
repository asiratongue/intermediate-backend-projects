from src.utils.logger_setup import logger
import os
import subprocess
from src.config import config_manager
from src.utils import restore_s3, connect_db
import sqlite3
import time
import gzip
import pandas
import shutil
from io import StringIO
from pathlib import Path

configs = config_manager.load_configs()
backup_list_path = Path(r"G:\\01101000111101\Programming\Projects\intermediate-backend-projects\Database_Backup_Utility\src\config")

# Helper function to provide compatibility for Python versions without str.removesuffix
def remove_suffix(text, suffix):
    """Remove suffix from string if it exists"""
    if text.endswith(suffix):
        return text[:-len(suffix)]
    return text

def restore(db_type : str):

    extracted_backup_dir = os.path.join(os.getcwd(), 'extracted_backup')
    if not os.path.exists(extracted_backup_dir):
        os.makedirs(extracted_backup_dir)

    env = os.environ.copy()
    env["PGSSLMODE"] = "prefer"
    env["PGPASSWORD"] = configs['postgresql']['password']

    list_dict = {"d" : "db_backup_list.txt", "t" : "table_backup_list.txt"}
    choice = input("please type [d] to restore an entire db, or [t] to restore selected table(s) ") 

    if choice != 'd' and choice != 't':
        logger.error("error: Invalid input, must be 'd' or 't'")
        return
  
    with open(Path(backup_list_path, list_dict[choice]), 'r') as file:
        lines = file.read().splitlines()
        file.seek(0)
        line_read = file.readlines()
        print(f"here all the backups currently available for {db_type}:\n")

        for line in line_read:
            if line.startswith(db_type):
                x = line.split()[1]
                print(x + "\n")

        backups = input(f"please choose which backup/tables you wish to restore to (please pick a table compatible with your {db_type} db!)")
        backups = backups.split()
        
        paths = [line.split()[1] for line in lines]
        if any(not any(backup == path for path in paths) for backup in backups):
            logger.info(f"paths : {paths}")
            logger.info(f"backups : {backups}")
            logger.error("error : invalid input, must select from one of the backups!")
            return
        
    for i, backup in enumerate(backups):
        if 's3://' in backup:
            logger.info(f"starting s3 process for {backup}")
            backups[i] = restore_s3(backups, extracted_backup_dir)
            logger.info(f"data location to restore from: {backups[0]}")

    """FULL RESTORE""" 
    if any(backups[0].endswith(ext) for ext in ['.sql', '.tar', '.gz']) and backups[0].endswith('csv.gz') == False:
        warning = input("restoring the database from backup will first delete your current one, once deleted this is IRREVERSIBLE, are you sure you want to continue? ([Y]es or [N]o)")

        if warning != 'Y':
            print("Aborted.")
            return
        
        if db_type == 'postgresql':
            backup = backups[0]
            clear_database = subprocess.run(['psql', '-h', configs["postgresql"]["host"], '-p', configs["postgresql"]['port'], '-U', configs["postgresql"]['user'], '-d', configs["postgresql"]['database'], 
                            '-c', 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'], capture_output=True, text=True, env=env)
            
            logger.info(f"clear database returncode : {clear_database.returncode}, clear database stderr : {clear_database.stderr}")

            if backups[0].endswith('.gz'):
                extracted_backup = backups[0].replace(".gz", "")
                logger.info(f"this is the extracted backup path at line 482: {extracted_backup}")

                with gzip.open(backups[0], 'rb') as f_in:
                    with open(extracted_backup, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        backup = extracted_backup

                        logger.info(f"this is the backup path: {backup}")
                        logger.info(f"this is the extracted backup path at line 489: {extracted_backup}")


            restore_db = subprocess.run(['psql', '-h', configs["postgresql"]["host"], '-p', configs["postgresql"]['port'], '-U', configs["postgresql"]['user'], '-d', configs["postgresql"]['database'], 
                                '-v', 'ON_ERROR_STOP=1', '-e' ,'-f', backup], capture_output=True, text=True, env=env)
            
            if backups[0].endswith('.gz') and os.path.exists(extracted_backup):
                    os.remove(extracted_backup)

            logger.info(f"restore_db returncode : {restore_db.returncode}, restore_db stderr : {restore_db.stderr}")


                      
        elif db_type == 'sqlite':
            source_path = str(configs["sqlite"]["path"])

            try:
                if os.path.exists(source_path):
                    os.remove(source_path)
                open(source_path, 'a').close()
                print("Database file cleared successfully")
            except Exception as e:
                logger.error(f"Error clearing database : {e}")

            if backups[0].endswith('.gz'):
                restore_db = False

                with gzip.open(backups[0], 'rb') as f_in:
                    sql_dump = f_in.read()
                    conn = sqlite3.connect(source_path)

                    try:
                        conn.executescript(sql_dump.decode('utf-8'))
                        print('SQL script extracted and executed')
                    except sqlite3.Error as e:
                        print(f"Error restoring database: {str(e)}")
            else:
                unzip_db = False
                restore_db = subprocess.run(['sqlite3', source_path, f'.read {backups[0]}'], capture_output=True, text=True)

            if restore_db == True and restore_db.returncode != 0:
                logger.error(f"Error backing up database")
                if unzip_db:
                    logger.error(f"{unzip_db.stderr}")  
                return logger.error(f"{restore_db.stderr}")
        
        elif db_type == 'mongodb':
            client, db = connect_db(db_type)
            db.command("dropDatabase")

            restore_string = f'{configs["mongodb"]["connection_string"]}/{configs["mongodb"]["database"]}'
            temp_dir = f"temp_extract_{(int(time.time()))}"
            tar_basename = os.path.basename(backups[0])
            db_basename = configs["mongodb"]["database"]

            if backups[0].endswith('.tar.gz'):
                tar_basename = tar_basename.replace('.gz', '')

            inner_tar = os.path.join(temp_dir, tar_basename, db_basename)
            print(inner_tar)

            try:
                os.makedirs(temp_dir, exist_ok=True)

                if backups[0].endswith('.tar.gz'):
                    subprocess.run(['tar', '-xzf', backups[0], '-C', temp_dir], check=True)
                    
                    restore_db = subprocess.run(['mongorestore', f'--uri={restore_string}', f'--dir={inner_tar}'], check=True)
                    logger.info(f"Restore result: {restore_db.stderr}, returncode: {restore_db.returncode}")
                elif backups[0].endswith('.gz'):
                    output_file = os.path.join(temp_dir, os.path.basename((backups[0])[:-3]))


                    with open(output_file, 'wb') as f_out:
                        result = subprocess.run(['gunzip', '-c', backups[0]], stdout=f_out, check=True)
                    restore_db = subprocess.run(['mongorestore', f'--uri={restore_string}', f'--dir={inner_tar}'], check=True)
                    logger.info(f"Restore result: {restore_db.stderr}, returncode: {restore_db.returncode}")
                elif backups[0].endswith('.tar'):
                    result = subprocess.run(['tar', '-xf', backups[0], '-C', temp_dir], check=True)
                    restore_db = subprocess.run(['mongorestore', f'--uri={restore_string}', f'--dir={inner_tar}'], check=True)
                    logger.info(f"Restore result: {restore_db.stderr}, returncode: {restore_db.returncode}")
                else:        
                    return logger.error("you must restore from a .tar or a .tar.gz")
                
            finally:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

    """.CSV TABLE RESTORE"""     
    if any(backups[0].endswith(ext) for ext in ['.csv','csv.gz']):

        warning = input("restoring selected tables from backup will first delete your current tables, once deleted this is IRREVERSIBLE, are you sure you want to continue? ([Y]es or [N]o)")
        if warning != 'Y':
            print("Aborted.")
            return  
              
        connection, mongodb = connect_db(db_type)

        """DECOMPRESSING A COMPRESSED .CSV"""
        for table_path in backups:
            datastore_string = table_path.basename(table_path).removesuffix(".csv")
            if 'extracted_backup' not in table_path:
                datastore_string = datastore_string.split('_', 2)[2]

            logger.info(f"current table_path : {table_path}")

            if table_path.endswith('.gz'):
                table_ext = table_path.replace('.gz', '')
                with gzip.open(table_path, 'rt') as f_in:
                    csv_content = f_in.read()
                    logger.info(f"csv content {csv_content}")
                with open(table_ext, 'w') as f_out:
                    f_out.write(csv_content)
                    table_path = table_ext

                    logger.info(f"table path after extraction : {table_path}")

            df = pandas.read_csv(table_path)

            if db_type == "postgresql" or db_type == "sqlite":
                cursor = connection.cursor()
                cursor.execute(f"SELECT EXISTS(SELECT 1 FROM \"{datastore_string}\" LIMIT 1)")

            if db_type == "postgresql":
                buffer = StringIO()
                df.to_csv(buffer, index=False, header=False,  quoting=1, na_rep='NULL')
                buffer.seek(0)
                if cursor.fetchone()[0]:
                    logger.info("table has data!")            
                    cursor.execute(f'TRUNCATE TABLE "{datastore_string}" CASCADE')

                cursor.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = \'{datastore_string}\' ORDER BY ordinal_position')
                db_columns = [col[0] for col in cursor.fetchall()]
                csv_columns = df.columns.tolist()


                try:
                    cursor.copy_expert(f'COPY "{datastore_string}" FROM STDIN WITH CSV', buffer)
                    connection.commit()

                except Exception as e:
                    connection.rollback()
                    print(f"Error loading {datastore_string}: {e}")

            elif db_type == "sqlite": 
                if cursor.fetchone()[0]:              
                    cursor.execute(f'DELETE FROM "{datastore_string}"')
                    connection.commit()
                df.to_sql(datastore_string, connection, if_exists='replace', index=False)

            elif db_type == "mongodb":
                collection = mongodb[datastore_string]
                collection.delete_many({})
                logger.info(f"Cleared the collection: {datastore_string}")                
                uri_string = '--uri=' + configs["mongodb"]["connection_string"] + f'/{configs["mongodb"]["database"]}'
                
                process = subprocess.run(['mongoimport', uri_string, "--db", configs["mongodb"]["database"], "--collection", datastore_string, "--type", "csv", "--file", table_path, "--headerline"], 
                               capture_output=True, text=True)
                
                if process.returncode != 0:
                    logger.error(f"error importing {table_path} : {process.stderr}")
                    return False

            if os.path.exists(table_path + '.gz'):
                os.remove(table_path)

            if os.path.exists(extracted_backup_dir):
                pass

    # if db_type == "postgresql" or db_type == "sqlite":                
    #     connection.commit()
    #     connection.close()
    #     cursor.close()
        
    print(f"{backups} restored successfully")
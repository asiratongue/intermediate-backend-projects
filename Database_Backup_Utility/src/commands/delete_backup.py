from utils.logger_setup import logger
from config import config_manager
import os
from pathlib import Path

configs = config_manager.load_configs()
backup_list_path = Path(r"G:\\01101000111101\Programming\Projects\intermediate-backend-projects\Database_Backup_Utility\src\config")

def delete():  

    choice = input("please type [d] to delete a db, or [t] for a table ")
    choice_dict = {"d" : Path(backup_list_path, "db_backup_list.txt"), "t" : Path(backup_list_path, "table_backup_list.txt")}

    if choice != "d" and choice != "t":
        logger.error("error : invalid input,  must be 'd' or 't'")
        return

    def print_backups(choice):
        with open(Path(backup_list_path, choice), 'r') as file:
            lines = file.read().splitlines()
            if not any(line.strip() for line in lines):
                return False
            print("here all the backups currently available:")
            for line in lines:
                x = line.split()[1]
                print(x)

            return(choice, lines)

    user_choice = print_backups(choice_dict[choice])
    if user_choice == False:
        return logger.info("there are no backups currently available! returning . . .")

    backups = input("please choose which backup you wish to delete, paste the path, and follow each with a space ")

    delete_list = backups.split()

    for file in delete_list:

        if "s3://" in file:
            parsed_url = file.replace("s3://", "")
            parts = parsed_url.split("/", 1)
            object_key = parts[1] if len(parts) > 1 else ""

            configs["s3_client"].delete_object(Bucket = configs["s3"]["BucketName"], Key = object_key)
            continue

        os.remove(file)
  
        print(f"{file} sucessfully deleted")

    new_lines = ["\n"+line for line in user_choice[1] if line.split()[1] not in [item.strip() for item in delete_list]]

    with open(user_choice[0], 'w') as file:
        file.writelines(new_lines)

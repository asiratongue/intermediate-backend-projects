import typer
from commands import backup_database, restore_database, view_database, delete_backup
from src.commands import connection_test

app = typer.Typer()

@app.command(name="test-connection", help="Test the connection of your configured database")
def connection_test_command(db_type: str = typer.Argument(help="choose the type of db you are checking connection to")):
    connection_test.connection_test(db_type)

@app.command(help="View all tables within your configured database")
def view(db: str = typer.Argument(help="Type of database to connect to (postgres, sqlite, mongodb)")):
    view_database.view(db)

@app.command(help = 'restore configured database from full sql dump or selected csv table')
def restore(db_type : str):
    restore_database.restore(db_type)

@app.command(help = "Delete any listed backups")
def delete():
    delete_backup.delete()    

@app.command(help = "Backup your configured database to selected location, choose between a full sql dump or individual csv tables")
def backup(db_type : str = typer.Argument(help="Type of database to back up (postgresql, sqlite, mongodb)"), 
           backup_path : str = typer.Argument(help="Full path to where the backup will be saved"),
           storage: str = typer.Argument(None, help="Back up to the configured cloud, saves locally first."),
           compression: int = typer.Option(10, "--compression", "-c", help = "Optionally choose data compression level.")
           ):
    backup_database.backup(db_type, backup_path, storage, compression)


if __name__ == "__main__":
    app()
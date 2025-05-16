import shutil
import os
from datetime import datetime

def backup_database(db_path='./instance/app.db', backup_dir='./instance/backups'):
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")
    print(backup_path)
    shutil.copy(db_path, backup_path)
    return backup_path


def restore_database(backup_file, db_path='./instance/app.db'):
    shutil.copy(backup_file, db_path)
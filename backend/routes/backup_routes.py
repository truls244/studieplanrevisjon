import os
from flask import Blueprint, jsonify, request
import logging
from scripts.backup import backup_database, restore_database

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   filename='database_operations.log')
logger = logging.getLogger(__name__)

# Create blueprint
backup_bp = Blueprint('backup', __name__)


# Define helper functions

@backup_bp.route('/backup', methods=['POST'])
def backup():
    try:
        backup_file = backup_database()
        return jsonify({'message': 'Backup successful', 'file': backup_file})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@backup_bp.route('/restore/<string:filename>', methods=['POST'])
def restore_backup(filename):

    backup_name = filename
    backup_path = os.path.join('./instance/backups', backup_name)
    print(backup_path)
    if not os.path.exists(backup_path):
        return jsonify({'error': 'Backup file not found'}), 404
    restore_database(backup_path)
    return jsonify({'message': 'Database restored successfully'})

@backup_bp.route('/backups', methods=['GET'])
def list_backups():
    try:
        files = os.listdir('./instance/backups')
        db_files = [f for f in files if f.endswith('.db')]
        return jsonify(sorted(db_files, reverse=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 500



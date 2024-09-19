from flask import Blueprint, request, jsonify
from src.modules.SW6.controller.SW6BackupController import SW6BackupController

from werkzeug.exceptions import BadRequest, NotFound

SW6BackupViews = Blueprint('sw6_backup_views', __name__)

"""
API
"""


@SW6BackupViews.route('/api/sw6/backup/db', methods=['POST', 'GET'])
def sw6_backup_db():
    result = SW6BackupController().backup_db()
    return jsonify(result)


@SW6BackupViews.route('/api/sw6/backup/files', methods=['POST', 'GET'])
def sw6_backup_files():
    result = SW6BackupController().backup_files()
    return jsonify(result)

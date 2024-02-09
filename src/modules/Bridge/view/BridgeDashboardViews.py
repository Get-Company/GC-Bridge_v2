from datetime import datetime, timedelta
from pprint import pprint
from src import db

from flask import Blueprint, jsonify, render_template, request, flash, redirect, url_for
from sqlalchemy import or_


BridgeDashboardViews = Blueprint('bridge_dashboard_views', __name__)


@BridgeDashboardViews.route('/', endpoint='dashboard')
def bridge_show_dashboard():
    return render_template('bridge/dashboard/dashboard.html')


"""
API
"""


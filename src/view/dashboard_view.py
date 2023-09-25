from flask import Blueprint, render_template

dashboard_view = Blueprint('dashboard_view', __name__)

@dashboard_view.route('/')
def index():
    return render_template('dashboard.html')

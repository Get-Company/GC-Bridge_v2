from flask import Blueprint, render_template
from ..modules.ERP.controller.ERPConnectionController import ERPConnectionController
from ..modules.ERP.controller.ERPDatasetController import ERPDatasetController

erp_obj = ERPConnectionController()
dataset_view = Blueprint('dataset_view', __name__)


@dataset_view.route('/')
def show_dataset():
    return render_template('erp/erp_base.html')

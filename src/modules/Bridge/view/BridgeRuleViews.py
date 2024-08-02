from flask import Blueprint, render_template
from src.modules.Bridge.controller.BridgeRuleController import BridgeRuleController

BridgeRuleViews = Blueprint('bridge_rule_views', __name__)


@BridgeRuleViews.route("/rules", endpoint='rules')
def bridge_show_rules():
    rules = BridgeRuleController().get_all()

    return render_template('bridge/rule/rules.html',
                           rules=rules)


@BridgeRuleViews.route("/rule/new", endpoint='rule_new')
def bridge_create_rule():
    sw6_endpoints = BridgeRuleController().sw6_get_endpoints()
    return render_template('bridge/rule/rule_new.html',
                           sw6_endpoints=sw6_endpoints)

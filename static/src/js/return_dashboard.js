// static/src/js/return_dashboard.js
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class ReturnDashboard extends Component {
    setup() {}

    open_action(action_name) {
        this.env.services.action.doAction(action_name);
    }
}
ReturnDashboard.template = "returns_management.return_dashboard_template";

// تسجيل الكومبوننت كـ Client Action
registry.category("actions").add("return_dashboard", ReturnDashboard);

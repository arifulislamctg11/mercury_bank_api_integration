# Copyright (c) 2025, Ariful Islam and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MercurySettings(Document):
    def validate(self):
        """Validate API key format when saving"""
        if self.api_key and not self.api_key.startswith("secret-token:"):
            frappe.throw("Invalid API key format. Mercury keys typically start with 'secret-token:'")
    
    def before_save(self):
        """Ensure only one settings record exists"""
        if self.is_new() and frappe.db.exists("Mercury Settings", "Mercury Settings"):
            frappe.throw("Only one Mercury Settings record can exist")
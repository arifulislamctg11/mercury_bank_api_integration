import frappe
import json

@frappe.whitelist(allow_guest=True)
def webhook():
    data = json.loads(frappe.request.data)
    frappe.logger().info(f"Webhook data: {data}")

    # Process incoming transaction or event
    # Example: Save transaction info in custom DocType
    return "OK"

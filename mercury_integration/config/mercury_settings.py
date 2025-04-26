from frappe import _

def get_data():
    return {
        "fieldname": "mercury_settings",
        "transactions": [
            {
                "label": _("Bank Accounts"),
                "items": ["Bank Account"]
            },
            {
                "label": _("Transactions"),
                "items": ["Bank Transaction"]
            }
        ]
    }
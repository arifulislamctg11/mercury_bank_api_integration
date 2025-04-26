import frappe
import requests
from frappe import _

# mercury_integration/mercury_integration/api.py

from frappe.utils import now_datetime

BASE_URL = "https://api.mercury.com/api/v1"

@frappe.whitelist()
def sync_mercury_accounts():
    try:
        settings = get_mercury_settings()
        if not settings.company:
            return {"success": False, "error": "Company not set in Mercury Settings"}
        
        headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "Accept": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/accounts", headers=headers)
        response.raise_for_status()
        
        accounts = response.json().get("accounts", [])
        results = {
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        for acc in accounts:
            success, message = create_or_update_bank_account(acc, settings.company)
            if success:
                results["created" if message == "created" else "updated"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "account": acc.get("nickname"),
                    "error": message
                })
        
        frappe.db.commit()
        return {
            "success": True,
            "results": results,
            "message": f"Synced {len(accounts)} accounts ({results['created']} new, {results['updated']} updated)"
        }
        
    except Exception as e:
        frappe.db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

def create_or_update_bank_account(acc_data, company_name):
    try:
        # Always use "Bank" as the account type since it's a valid option
        account_type = "Bank"
        
        bank_account_id = f"Mercury-{acc_data['id']}"
        account_name = f"{acc_data['nickname']} - {acc_data['accountNumber'][-4:]}"
        parent_account = "Bank Accounts - MSB"
        
        # 1. Create Account in Chart of Accounts
        if not frappe.db.exists("Account", {"account_name": account_name, "company": company_name}):
            account = frappe.new_doc("Account")
            account.update({
                "account_name": account_name,
                "parent_account": parent_account,
                "company": company_name,
                "account_type": account_type,  # Using "Bank" type
                "account_currency": "USD",
                "is_group": 0
            })
            account.insert(ignore_permissions=True)
            print(f"Created Account: {account_name}")
        
        # 2. Create Bank Account record
        bank_account_data = {
            "account_name": account_name,
            "bank": "Mercury",
            "account_type": account_type,  # Using "Bank" type here too
            "account_number": acc_data["accountNumber"],
            "routing_number": acc_data["routingNumber"],
            "bank_account_no": acc_data["accountNumber"],
            "company": company_name,
            "is_company_account": 1,
            "integration_id": acc_data["id"]
        }
        
        if not frappe.db.exists("Bank Account", bank_account_id):
            bank_account = frappe.new_doc("Bank Account")
            bank_account.update(bank_account_data)
            bank_account.insert(ignore_permissions=True)
            print(f"Created Bank Account: {bank_account_id}")
            return True, "created"
        else:
            bank_account = frappe.get_doc("Bank Account", bank_account_id)
            bank_account.update(bank_account_data)
            bank_account.save()
            print(f"Updated Bank Account: {bank_account_id}")
            return True, "updated"
            
    except Exception as e:
        error_msg = f"Failed to sync account {acc_data.get('id')}: {str(e)}"
        print(error_msg)
        frappe.log_error(title="Mercury Sync Error", message=error_msg)
        return False, str(e)



def get_mercury_settings():
    """Get or create Mercury Settings"""
    if not frappe.db.exists("Mercury Settings", "Mercury Settings"):
        settings = frappe.new_doc("Mercury Settings")
        settings.save()
    return frappe.get_doc("Mercury Settings", "Mercury Settings")
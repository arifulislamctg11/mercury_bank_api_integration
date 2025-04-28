import frappe
import requests
from frappe.utils import cint

class MercuryClient:
    def __init__(self):
        self.settings = frappe.get_cached_doc("Mercury Settings")
        self.base_url = "https://api.mercury.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.settings.get_password('api_key')}",
            "Accept": "application/json"
        }
        self.timeout = 30  # seconds

    def get_transactions(self, account_id, limit=500):
        """Safe API request with retry logic"""
        url = f"{self.base_url}/account/{account_id}/transactions"
        params = {"limit": cint(limit), "order": "desc"}
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("transactions", [])
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Mercury API failed for account {account_id}: {str(e)}"
            if hasattr(e, "response"):
                error_msg += f" | Response: {e.response.text}"
            frappe.log_error("Mercury API Error", error_msg)
            return []
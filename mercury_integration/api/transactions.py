import frappe
from frappe import _
from frappe.utils import nowdate, getdate ,now_datetime
from erpnext.accounts.doctype.bank_transaction.bank_transaction import BankTransaction
from .client import MercuryClient  # Import the API client



@frappe.whitelist()
def sync_mercury_transactions():
    """Sync transactions with comprehensive error handling"""
    try:
        mercury_accounts = frappe.get_all("Bank Account",
            filters={"integration_id": ["!=", ""]},
            fields=["name", "integration_id"]
        )
        
        if not mercury_accounts:
            frappe.log_error("No Mercury-connected accounts found", "Mercury Sync")
            return {"success": False, "message": "No connected accounts"}

        client = MercuryClient()
        results = {"success": True, "synced": 0, "errors": []}

        for account in mercury_accounts:
            try:
                transactions = client.get_transactions(account.integration_id)
                if not transactions:
                    continue

                for txn in transactions:
                    try:
                        if create_erpnext_bank_transaction(txn, account):
                            results["synced"] += 1
                    except Exception as txn_error:
                        error_msg = f"Failed on transaction {txn.get('id')}: {str(txn_error)}"
                        results["errors"].append(error_msg)
                        frappe.log_error(error_msg)

            except Exception as account_error:
                error_msg = f"Account {account.name} failed: {str(account_error)}"
                results["errors"].append(error_msg)
                frappe.log_error(error_msg)

        frappe.db.commit()
        results["message"] = f"Synced {results['synced']} transactions"
        return results

    except Exception as global_error:
        frappe.db.rollback()
        frappe.log_error("Mercury sync failed completely", str(global_error))
        return {"success": False, "message": str(global_error)}


def create_erpnext_bank_transaction(txn_data, bank_account):
    """Safe transaction creation with validation"""
    # Validate required fields
    required_fields = ["id", "createdAt", "amount", "kind"]
    if not all(field in txn_data for field in required_fields):
        raise ValueError(f"Missing required fields in: {txn_data}")

    # Check for duplicates
    if frappe.db.exists("Bank Transaction", {
        "reference_number": txn_data["id"],
        "bank_account": bank_account.name
    }):
        return False

    try:
        doc = frappe.new_doc("Bank Transaction")
        is_deposit = float(txn_data["amount"]) >= 0
        
        # Handle party safely
        party_name = txn_data.get("counterpartyName")
        party_type = None
        if party_name:
            party_type = "Customer" if is_deposit else "Supplier"
            if not frappe.db.exists(party_type, party_name):
                party_name = None  # Skip if party doesn't exist

        doc.update({
            "date": getdate(txn_data["createdAt"]),
            "bank_account": bank_account.name,
            "deposit" if is_deposit else "withdrawal": abs(float(txn_data["amount"])),
            "reference_number": txn_data["id"],
            "description": txn_data.get("bankDescription") or txn_data["kind"],
            "transaction_type": txn_data["kind"].title(),
            "party_type": party_type,
            "party": party_name,
            "unallocated_amount": abs(float(txn_data["amount"]))
        })

        doc.insert(ignore_permissions=True)
        return True

    except Exception as e:
        error_msg = f"Failed to create transaction {txn_data.get('id')}: {str(e)}"
        frappe.log_error(error_msg)
        raise  # Re-raise for outer handling



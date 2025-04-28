// Copyright (c) 2025, Ariful Islam and contributors
// For license information, please see license.txt
// Copyright (c) 2025, Ariful Islam and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mercury Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__('Sync Accounts'), function() {
            frappe.call({
                method: "mercury_integration.api.accounts.sync_mercury_accounts",
                args: {},
                callback: function(response) {
                    if (response.message && response.message.success) {
                        frappe.show_alert({
                            message: __("Synced accounts: {0} created, {1} updated",
                                response.message.results.created, response.message.results.updated),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Sync Failed'),
                            indicator: 'red',
                            message: __("Error: {0}", response.message ? (response.message.error || "Unknown error") : "Unknown error")
                        });
                    }
                    frm.refresh();
                },
                freeze: true,
                freeze_message: __("Syncing accounts...")
            });
        });

        frm.add_custom_button(__('Sync Mercury Transactions'), function() {
            frappe.call({
                method: 'mercury_integration.api.transactions.sync_mercury_transactions',
                args: {
                    bank_account: frm.doc.name
                },
                callback: function(r) {
                    if (r.message && r.message.count !== undefined) {
                        frappe.show_alert({
                            message: __("Synced {0} transactions", [r.message.count]),
                            indicator: 'green'
                        });
                        frappe.set_route('List', 'Bank Transaction');
                    } else {
                        frappe.msgprint({
                            title: __('Transaction Sync Failed'),
                            indicator: 'red',
                            message: __("Error during transaction sync.")
                        });
                    }
                }
            });
        }, __("Actions")); // The label should be the third argument to add_custom_button
    }
});
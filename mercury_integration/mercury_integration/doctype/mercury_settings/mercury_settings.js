// Copyright (c) 2025, Ariful Islam and contributors
// For license information, please see license.txt

frappe.ui.form.on("Mercury Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__('Sync Accounts'), function() {
            frappe.call({
                method: "mercury_integration.api.sync_mercury_accounts",
                args: {},
                callback: function(response) {
                    if (response.message.success) {
                        frappe.show_alert({
                            message: __("Synced accounts", 
                                      response.message.results.created + response.message.results.updated),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Sync Failed'),
                            indicator: 'red',
                            message: __("Error: {0}", response.message.error || "Unknown error")
                        });
                    }
                    frm.refresh();
                },
                freeze: true,
                freeze_message: __("Syncing accounts...")
            });
        }, __("Actions"));
    }
});
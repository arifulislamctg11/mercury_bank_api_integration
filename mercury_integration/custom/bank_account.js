// mercury_integration/custom/bank_account.js
frappe.ui.form.on('Bank Account', {
    refresh(frm) {
        if(frm.doc.integration_id) {
            frm.add_custom_button(__('Sync Mercury Transactions'), function() {
                frappe.call({
                    method: 'mercury_integration.api.transactions.sync_mercury_transactions',
                    args: {
                        bank_account: frm.doc.name
                    },
                    callback: function(r) {
                        frappe.show_alert({
                            message: __("Synced {0} transactions", [r.message.count]),
                            indicator: 'green'
                        });
                        frappe.set_route('List', 'Bank Transaction');
                    }
                });
            }, __('Mercury'));
            
        }
    }
});
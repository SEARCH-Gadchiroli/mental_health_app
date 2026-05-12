// Copyright (c) 2026, SEARCH Gadchiroli and contributors
// For license information, please see license.txt

frappe.ui.form.on("MH External Review", {

    refresh: function(frm) {
        // Hide source fields from the reviewer — only visible after submit
        if (!frm.doc.is_revealed) {
            frm.set_df_property("output_1_source", "hidden", 1);
            frm.set_df_property("output_2_source", "hidden", 1);
            frm.set_df_property("blind_assignment", "hidden", 1);
            frm.set_df_property("revealed_output_1_label", "hidden", 1);
            frm.set_df_property("revealed_output_2_label", "hidden", 1);
        }

        // Validate scores before submit
        if (frm.doc.docstatus === 0 && !frm.doc.__islocal) {
            frm.add_custom_button(__("Submit Review"), function() {
                if (!validate_scores(frm)) return;
                frm.savesubmit();
            }, __("Actions"));
        }
    },

    validate: function(frm) {
        validate_scores(frm);
    }

});


function validate_scores(frm) {
    const fields = [
        "output_1_psychoed_score",
        "output_2_psychoed_score"
    ];

    for (const field of fields) {
        const val = frm.doc[field];
        if (val !== undefined && val !== null && val !== "") {
            if (val < 1 || val > 10) {
                frappe.msgprint({
                    title: __("Invalid Score"),
                    message: __("All scores must be between 1 and 10."),
                    indicator: "red"
                });
                return false;
            }
        }
    }
    return true;
}

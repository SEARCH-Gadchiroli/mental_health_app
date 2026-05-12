frappe.ui.form.on("MH External Review", {
    consultation: function(frm) {
        if (frm.doc.consultation) {
            fetch_and_randomize(frm);
        }
    },

    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            show_reveal_info(frm);
        }
    },

    on_submit: function(frm) {
        // Show a popup message immediately on submission
        show_reveal_info(frm);
    }
});

function fetch_and_randomize(frm) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "MH_Chatbot_Consultation_Glific",
            name: frm.doc.consultation
        },
        callback: function(r) {
            if (r.message) {
                const con = r.message;
                const is_ai_first = Math.random() < 0.5;
                
                frm.set_value({
                    "blind_assignment": is_ai_first ? "AI_FIRST" : "DOCTOR_FIRST",
                    "output_1_source": is_ai_first ? "AI" : "Doctor",
                    "output_2_source": is_ai_first ? "Doctor" : "AI",
                    "output_1_psychoed_text": is_ai_first ? con.ai_diagnosis_output : con.doctor_diagnosis_output,
                    "output_2_psychoed_text": is_ai_first ? con.doctor_diagnosis_output : con.ai_diagnosis_output
                });
            }
        }
    });
}

function show_reveal_info(frm) {
    const s1 = frm.doc.output_1_source || "Unknown";
    const s2 = frm.doc.output_2_source || "Unknown";

    // 1. Show as a message box
    frappe.msgprint({
        title: __("Sources Revealed"),
        indicator: "green",
        message: `
            <div style="font-size: 1.1em;">
                <p><b>Output 1:</b> ${s1}</p>
                <p><b>Output 2:</b> ${s2}</p>
            </div>
        `
    });

    // 2. Try to update the labels on the form for reference
    frm.set_df_property("revealed_output_1_label", "options", s1);
    frm.set_df_property("revealed_output_2_label", "options", s2);
}

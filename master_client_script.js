// ── Field names ────────────────────────────────────────────────
const DOCTYPE            = "MH_Chatbot_Consultation_Glific";
const SOURCE_FIELD       = "ai_diagnosis_output";
const AI_SCREENING_FIELD = "ai_screening_output";
const AI_DIAGNOSIS_FIELD = "ai_diagnosis_output_1";

// ── Frappe hooks ───────────────────────────────────────────────
frappe.ui.form.on(DOCTYPE, {
    refresh: function(frm) {
        // 1. Auto-populate on refresh
        if (frm.doc.docstatus === 0) {
            populateMHOutputs(frm);
        }

        // 2. Add Similarity Calculation button
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Calculate Similarity Scores"), function() {
                
                // Safety check: record must be saved
                if (frm.is_new()) {
                    frappe.msgprint({
                        title: __("Save Required"),
                        message: __("Please save the document before calculating similarity scores."),
                        indicator: "orange"
                    });
                    return;
                }

                // Call server
                frappe.show_alert({ message: __("Contacting OpenAI..."), indicator: "blue" }, 5);
                
                frappe.call({
                    method: "mental_health.mental_health_department.api.calculate_similarity_scores",
                    args: { docname: frm.doc.name },
                    freeze: true,
                    freeze_message: __("Translating and Calculating..."),
                    callback: function(r) {
                        if (r.exc) {
                            frappe.msgprint({ title: __("API Error"), message: r.exc, indicator: "red" });
                            return;
                        }
                        
                        if (r.message) {
                            const scores = r.message;
                            const updates = {};
                            if (scores.pharmacotherapy_score !== null) updates["pharmacotherapy_similarity_score"] = scores.pharmacotherapy_score;
                            if (scores.diagnosis_score !== null) updates["diagnosis_similarity_score"] = scores.diagnosis_score;
                            
                            if (Object.keys(updates).length) {
                                frm.set_value(updates).then(() => {
                                    frm.save_or_update();
                                    frappe.show_alert({ message: __("Similarity Scores Updated Successfully"), indicator: "green" }, 5);
                                });
                            } else {
                                frappe.msgprint({
                                    title: __("Insufficient Data"),
                                    message: __("Please ensure both AI and Doctor outputs are filled for Diagnosis or Pharmacotherapy."),
                                    indicator: "orange"
                                });
                            }
                        }
                    }
                });
            });
        }
    },

    // Trigger when the AI text is updated
    ai_diagnosis_output: function(frm) {
        populateMHOutputs(frm);
    },

    // 3. Fetch Counselor Name from Master
    counselor_phone_number: function(frm) {
        if (frm.doc.counselor_phone_number) {
            frappe.db.get_value("MH Counselor", frm.doc.counselor_phone_number, "counselor_name", (r) => {
                if (r && r.counselor_name) {
                    frm.set_value("counselor_name", r.counselor_name);
                }
            });
        }
    }
});

// ── Helper: Auto-populate ───────────────────────────────────────
function populateMHOutputs(frm) {
    const text = frm.doc[SOURCE_FIELD];
    if (!text || !text.trim()) return;
    if (frm.doc[AI_SCREENING_FIELD] && frm.doc[AI_DIAGNOSIS_FIELD]) return;

    // Extract scores
    const scores = {};
    ["PHQ-9", "GAD-7", "PADIS"].forEach(tool => {
        const escaped = tool.replace("-", "\\-");
        const rx = new RegExp(escaped + "[^\\d]{0,20}(\\d+)", "i");
        const m = text.match(rx);
        if (m) scores[tool] = m[1];
    });

    // Extract conditions (Simplified version for efficiency)
    const conditions = [];
    const bracketPattern = /([^\(,،।\n]{3,50}?)\s*\(\s*(PHQ[-]?9|GAD[-]?7|PADIS)[^)]*\)/gi;
    let m;
    while ((m = bracketPattern.exec(text)) !== null) {
        const cond = m[1].trim().replace(/^[,،।\s]+|[,،।\s]+$/g, "").trim();
        if (cond.length > 1) conditions.push(cond);
    }

    const screeningLines = [];
    if (scores["PHQ-9"]) {
        screeningLines.push(`PHQ-9: ${scores["PHQ-9"]}`);
        if (!frm.doc.phq_overall_score) frm.set_value("phq_overall_score", scores["PHQ-9"]);
    }
    if (scores["GAD-7"]) {
        screeningLines.push(`GAD-7: ${scores["GAD-7"]}`);
        if (!frm.doc.gad_overall_score) frm.set_value("gad_overall_score", scores["GAD-7"]);
    }
    if (scores["PADIS"]) {
        screeningLines.push(`PADIS: ${scores["PADIS"]}`);
        if (!frm.doc.padis_overall_score) frm.set_value("padis_overall_score", scores["PADIS"]);
    }

    if (!frm.doc[AI_SCREENING_FIELD] && screeningLines.length) {
        frm.set_value(AI_SCREENING_FIELD, "Screening Scores:\n" + screeningLines.join("\n"));
    }

    if (!frm.doc[AI_DIAGNOSIS_FIELD] && conditions.length) {
        frm.set_value(AI_DIAGNOSIS_FIELD, "Diagnosis:\n" + conditions.map(c => `- ${c}`).join("\n"));
    }
}

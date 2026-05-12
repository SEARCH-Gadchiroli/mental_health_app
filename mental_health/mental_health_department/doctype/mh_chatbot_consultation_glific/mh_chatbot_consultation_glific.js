// Copyright (c) 2026, SEARCH Gadchiroli and contributors
// For license information, please see license.txt

// Client-side logic for MH_Chatbot_Consultation_Glific is managed
// via Client Scripts in the Frappe database:
//   - Mental_Health_Role_Visiblity  → tab visibility per role
//   - Mental_health_auto_populate   → parse AI output into structured fields
//   - similarity_score              → calculate AI vs Doctor similarity via server API

frappe.ui.form.on("MH_Chatbot_Consultation_Glific", {
	// refresh: function(frm) {}
});

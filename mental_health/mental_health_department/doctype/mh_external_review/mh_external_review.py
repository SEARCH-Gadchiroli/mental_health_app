# Copyright (c) 2026, SEARCH Gadchiroli and contributors
# For license information, please see license.txt
"""
Controller for MH External Review DocType.

Handles:
  - Randomized blind output assignment (server-side, persists in DB)
  - Populating Output 1 / Output 2 text from the linked consultation
  - Revealing sources (AI vs Doctor) after submission
"""

import random
import frappe
from frappe.model.document import Document


class MHExternalReview(Document):

    def before_insert(self):
        """
        On first save: randomly assign AI vs Doctor outputs to Output 1 / Output 2.
        The assignment is stored in `blind_assignment` and never changes.
        """
        self._populate_blind_outputs()

    def on_submit(self):
        """
        After submission: reveal which output was AI vs Doctor.
        """
        self._reveal_sources()

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _populate_blind_outputs(self):
        """
        Fetch AI and Doctor outputs from the linked consultation,
        randomly assign to Output 1 / Output 2, and store the mapping.
        """
        if not self.consultation:
            return

        consultation = frappe.get_doc("MH_Chatbot_Consultation_Glific", self.consultation)

        # Psychoeducation outputs
        ai_psychoed = (
            getattr(consultation, "ai_psychoeducation_output", None)
            or getattr(consultation, "ai_pharmacotherapy_output", None)
            or ""
        )
        doc_psychoed = (
            getattr(consultation, "doctor_psychoeducation_output", None)
            or getattr(consultation, "doctor_pharmacotherapy_output", None)
            or ""
        )

        # 50/50 random assignment — server-side so it cannot be manipulated
        if random.random() < 0.5:
            self.blind_assignment = "AI_FIRST"
            self.output_1_source = "AI"
            self.output_2_source = "Doctor"
            self.output_1_psychoed_text = ai_psychoed
            self.output_2_psychoed_text = doc_psychoed
        else:
            self.blind_assignment = "DOCTOR_FIRST"
            self.output_1_source = "Doctor"
            self.output_2_source = "AI"
            self.output_1_psychoed_text = doc_psychoed
            self.output_2_psychoed_text = ai_psychoed

    def _reveal_sources(self):
        """
        Set human-readable labels for Output 1 and Output 2 after submission.
        Stored so reviewers (and admins) can see results without re-computing.
        """
        if self.blind_assignment == "AI_FIRST":
            self.revealed_output_1_label = "AI Output"
            self.revealed_output_2_label = "Doctor Output"
        else:
            self.revealed_output_1_label = "Doctor Output"
            self.revealed_output_2_label = "AI Output"

        self.is_revealed = 1
        # Save without triggering submit again
        self.db_update()

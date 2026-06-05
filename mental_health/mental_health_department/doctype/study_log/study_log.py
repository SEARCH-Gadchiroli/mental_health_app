# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StudyLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		consent_sheet_filled: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		date: DF.Date | None
		doctor_response_sheet_filled: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		doctor_wrote_all_4_things: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		free_medicines_given: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		glific_issue: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		issue_sheet_filled: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		name: DF.Int | None
		patient_name: DF.Data | None
		registration_number: DF.Data | None
		serial_number: DF.Data | None
		visited_doctor: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
	# end: auto-generated types

	pass

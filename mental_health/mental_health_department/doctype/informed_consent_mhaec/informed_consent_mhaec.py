# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class InformedConsentMHAEC(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		consent_taken_by: DF.Data | None
		consent_type: DF.Literal["\u092e\u094c\u0916\u093f\u0915", "\u0932\u0947\u0916\u0940"]
		copy_given: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		date: DF.Date | None
		info_sheet_given: DF.Literal["\u0939\u094b\u092f", "\u0928\u093e\u0939\u0940"]
		name: DF.Int | None
		patient_name: DF.Data | None
		registration_number: DF.Data | None
		serial_number: DF.Data | None
		witness: DF.Data | None
	# end: auto-generated types

	pass

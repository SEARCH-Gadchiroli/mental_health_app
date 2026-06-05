# Copyright (c) 2026, SEARCH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AdverseEventRegister(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		adverse_event: DF.SmallText | None
		classification: DF.Data | None
		date: DF.Date | None
		name: DF.Int | None
		patient_name: DF.Data | None
		registration_number: DF.Data | None
		reported_by: DF.Data | None
		reporting_done: DF.Literal["Yes", "No"]
		reporting_required_to: DF.Data | None
		serial_number: DF.Data | None
		time_taken: DF.Data | None
		who_did_reporting: DF.Data | None
	# end: auto-generated types

	pass

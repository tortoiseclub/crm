import frappe
from frappe.model.document import Document


class FeedbackFormQuestion(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		question_label: DF.Data
		question_code: DF.Data | None
		question_type: DF.Literal["Select", "Text"]
		is_mandatory: DF.Check
		options_raw: DF.SmallText | None
	# end: auto-generated types

	pass


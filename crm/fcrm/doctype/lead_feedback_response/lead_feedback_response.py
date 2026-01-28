from frappe.model.document import Document


class LeadFeedbackResponse(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		question: DF.Link | None
		question_label: DF.Data | None
		question_type: DF.Data | None
		is_mandatory: DF.Check
		question_options_raw: DF.SmallText | None
		answer_choice: DF.Data | None
		answer_text: DF.SmallText | None
		answer_value: DF.Data | None
		answer_label: DF.Data | None
	# end: auto-generated types

	pass


import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class LeadFeedback(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		lead: DF.Link
		feedback_form: DF.Link
		status: DF.Literal["Draft", "Submitted", "Cancelled"]
		submitted_on: DF.Datetime | None
		submitted_by: DF.Link | None
		external_token: DF.Data | None
	# end: auto-generated types

	def before_insert(self):
		if not self.external_token:
			self.external_token = frappe.generate_hash(length=20)

	def validate(self):
		# Populate responses from template if needed
		if self.feedback_form and not self.responses:
			self._load_questions_from_template()

		self._validate_responses()

	def before_submit(self):
		self._set_submission_meta()

	def _load_questions_from_template(self):
		template = frappe.get_doc("Feedback Form", self.feedback_form)
		self.responses = []

		for q in template.questions:
			self.append(
				"responses",
				{
					"question": q.name,
					"question_label": q.question_label,
					"question_type": q.question_type,
					"is_mandatory": q.is_mandatory,
				},
			)

	def _set_submission_meta(self):
		self.submitted_on = now_datetime()
		if frappe.session.user:
			self.submitted_by = frappe.session.user

	def _validate_responses(self):
		"""Ensure mandatory questions are answered and Select answers are valid."""
		for resp in self.responses:
			question = frappe.get_doc("Feedback Form Question", resp.question)

			# Work with an effective answer coming from UI fields
			if question.question_type == "Select":
				effective_answer = (resp.answer_choice or resp.answer_value or resp.answer_label or "").strip()
			else:
				effective_answer = (resp.answer_text or resp.answer_value or resp.answer_label or "").strip()

			# Mandatory check
			if question.is_mandatory and not effective_answer:
				frappe.throw(
					frappe._("Please answer the question: {0}").format(question.question_label)
				)

			# For Select type, answer must be one of options_raw
			if question.question_type == "Select" and question.options_raw:
				valid_values = {
					line.strip()
					for line in question.options_raw.splitlines()
					if line.strip()
				}
				if effective_answer and effective_answer not in valid_values:
					frappe.throw(
						frappe._(
							"Invalid answer '{0}' for question '{1}'. It must be one of: {2}"
						).format(effective_answer, question.question_label, ", ".join(sorted(valid_values)))
					)

				# Normalize storage for Select answers
				resp.answer_value = effective_answer
				resp.answer_label = effective_answer
			else:
				# Normalize storage for Text answers
				resp.answer_value = effective_answer
				resp.answer_label = effective_answer


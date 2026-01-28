import frappe
from frappe import _
from frappe.utils import cint


@frappe.whitelist()
def get_feedback_templates():
	"""Return Feedback Form templates that can be used for CRM Lead feedback."""
	templates = frappe.get_all(
		"Feedback Form",
		filters={"is_published": 1, "applicable_for": "CRM Lead"},
		fields=["name", "description"],
		order_by="modified desc",
	)

	return [
		{
			"name": t.name,
			"label": t.name,
			"description": t.description or "",
		}
		for t in templates
	]


@frappe.whitelist()
def get_feedback_summary(lead: str):
	"""Return existing Lead Feedback records for a given lead."""
	if not lead:
		frappe.throw(_("Lead is required"))

	records = frappe.get_all(
		"Lead Feedback",
		filters={"lead": lead},
		fields=[
			"name",
			"feedback_form",
			"status",
			"submitted_on",
			"submitted_by",
			"external_token",
		],
		order_by="creation desc",
	)

	def get_template_label(feedback_form: str | None) -> str | None:
		if not feedback_form:
			return None
		return frappe.db.get_value("Feedback Form", feedback_form, "name") or feedback_form

	for row in records:
		row["feedback_form_label"] = get_template_label(row.get("feedback_form"))

	return records


@frappe.whitelist()
def create_lead_feedback(lead: str, feedback_form: str):
	"""Create a new Lead Feedback doc for a given lead and template."""
	if not lead:
		frappe.throw(_("Lead is required"))
	if not feedback_form:
		frappe.throw(_("Feedback Form is required"))

	doc = frappe.new_doc("Lead Feedback")
	doc.lead = lead
	doc.feedback_form = feedback_form

	# validate() will populate responses from the template and run basic checks
	doc.insert()

	return _serialize_feedback_with_questions(doc)


@frappe.whitelist()
def get_feedback_detail(name: str):
	"""Fetch a Lead Feedback document and its questions/answers for editing."""
	if not name:
		frappe.throw(_("Lead Feedback name is required"))

	doc = frappe.get_doc("Lead Feedback", name)
	return _serialize_feedback_with_questions(doc)


@frappe.whitelist()
def update_feedback_responses(name: str, responses, submit: int | str | None = None):
	"""Update answers for a Lead Feedback and optionally submit it.

	Args:
	        name: Lead Feedback name.
	        responses: JSON string or list of { rowname, value } objects.
	        submit: truthy value to submit after saving.
	"""
	if not name:
		frappe.throw(_("Lead Feedback name is required"))

	doc = frappe.get_doc("Lead Feedback", name)

	if isinstance(responses, str):
		responses = frappe.parse_json(responses or "[]")

	if not isinstance(responses, (list, tuple)):
		frappe.throw(_("Responses must be a list"))

	by_rowname = {row.get("rowname"): row for row in responses if row.get("rowname")}

	for resp in doc.responses:
		row = by_rowname.get(resp.name)
		if not row:
			continue

		raw_value = (row.get("value") or row.get("answer") or "").strip()

		if not resp.question:
			# If for some reason the link is missing, treat as free-text
			resp.answer_text = raw_value or None
			resp.answer_choice = None
			continue

		question = frappe.get_doc("Feedback Form Question", resp.question)

		if question.question_type == "Select":
			# Let LeadFeedback._validate_responses normalize to answer_value/answer_label
			resp.answer_choice = raw_value or None
			resp.answer_text = None
		else:
			resp.answer_text = raw_value or None
			resp.answer_choice = None

	# Save or submit – validation (including mandatory checks) runs in validate()
	if cint(submit):
		# Mark as submitted so validation runs in strict mode
		doc.status = "Submitted"
		doc.submit()
	else:
		doc.save()

	return _serialize_feedback_with_questions(doc)


@frappe.whitelist()
def discard_feedback(name: str):
	"""Delete a draft Lead Feedback document.

	Args:
	        name: Lead Feedback name.
	"""
	if not name:
		frappe.throw(_("Lead Feedback name is required"))

	doc = frappe.get_doc("Lead Feedback", name)

	# Only allow discarding drafts
	if doc.status != "Draft":
		frappe.throw(
			_("Only draft feedback can be discarded. Submitted feedback cannot be deleted.")
		)

	frappe.delete_doc("Lead Feedback", name, ignore_permissions=False)

	return {"success": True}


def _serialize_feedback_with_questions(doc):
	"""Return a serializable structure for Lead Feedback and its questions."""
	questions = []

	for resp in doc.responses:
		question = None
		if resp.question:
			question = frappe.get_doc("Feedback Form Question", resp.question)

		options = []
		if question and question.question_type == "Select" and question.options_raw:
			for line in question.options_raw.splitlines():
				line = line.strip()
				if not line:
					continue
				options.append({"label": line, "value": line})

		if (question and question.question_type == "Select") or resp.question_type == "Select":
			current_value = (
				(resp.answer_choice or resp.answer_value or resp.answer_label or "")
				if hasattr(resp, "answer_choice")
				else (resp.answer_value or resp.answer_label or "")
			)
		else:
			current_value = (
				(resp.answer_text or resp.answer_value or resp.answer_label or "")
				if hasattr(resp, "answer_text")
				else (resp.answer_value or resp.answer_label or "")
			)

		questions.append(
			{
				"rowname": resp.name,
				"question": resp.question,
				"label": resp.question_label,
				"type": question.question_type if question else resp.question_type,
				"is_mandatory": bool(getattr(resp, "is_mandatory", False)),
				"options": options,
				"value": (current_value or "").strip(),
			}
		)

	return {
		"feedback": {
			"name": doc.name,
			"lead": doc.lead,
			"feedback_form": doc.feedback_form,
			"status": doc.status,
			"submitted_on": doc.submitted_on,
			"submitted_by": doc.submitted_by,
			"external_token": doc.external_token,
		},
		"responses": questions,
	}


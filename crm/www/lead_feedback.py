import frappe

no_cache = 1


def get_context(context):
	token = frappe.form_dict.get("token")
	if not token:
		frappe.throw("Missing token")

	lead_feedback = frappe.get_doc("Lead Feedback", {"external_token": token})

	if frappe.request.method == "POST":
		_update_feedback_from_form(lead_feedback)
		context.success = True
	else:
		context.success = False

	questions = []
	for resp in lead_feedback.responses:
		question = frappe.get_doc("Feedback Form Question", resp.question)
		options = []
		if question.question_type == "Select" and question.options_raw:
			for line in question.options_raw.splitlines():
				line = line.strip()
				if not line:
					continue
				options.append({"label": line, "value": line})

		questions.append(
			{
				"rowname": resp.name,
				"label": resp.question_label,
				"type": resp.question_type,
				"is_mandatory": resp.is_mandatory,
				"options": options,
				"current_answer": resp.answer_label or resp.answer_value,
			}
		)

	context.lead_feedback = lead_feedback
	context.questions = questions


def _update_feedback_from_form(lead_feedback):
	for resp in lead_feedback.responses:
		fieldname = f"answer_{resp.name}"
		raw_value = frappe.form_dict.get(fieldname)
		if raw_value is None:
			continue

		question = frappe.get_doc("Feedback Form Question", resp.question)

		# For now, value and label are the same (parsed from options_raw or free text)
		resp.answer_value = raw_value
		resp.answer_label = raw_value

	lead_feedback.status = "Submitted"
	lead_feedback.save(ignore_permissions=True)



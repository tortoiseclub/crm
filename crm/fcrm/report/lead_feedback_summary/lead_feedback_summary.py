import frappe


def execute(filters=None):
	columns = [
		{"label": "Lead", "fieldname": "lead", "fieldtype": "Link", "options": "CRM Lead", "width": 180},
		{
			"label": "Feedback Form",
			"fieldname": "feedback_form",
			"fieldtype": "Link",
			"options": "Feedback Form",
			"width": 200,
		},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": "Submitted On", "fieldname": "submitted_on", "fieldtype": "Datetime", "width": 160},
		{"label": "Submitted By", "fieldname": "submitted_by", "fieldtype": "Link", "options": "User", "width": 160},
	]

	data = frappe.db.sql(
		"""
		SELECT
			lead,
			feedback_form,
			status,
			submitted_on,
			submitted_by
		FROM `tabLead Feedback`
		ORDER BY submitted_on DESC
		""",
		as_dict=True,
	)

	return columns, data


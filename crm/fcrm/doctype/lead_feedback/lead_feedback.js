frappe.ui.form.on("Lead Feedback", {
  onload(frm) {
    // For new docs, pre-populate responses when feedback_form is already set
    if (frm.is_new() && frm.doc.feedback_form && !frm.doc.responses?.length) {
      frm.trigger("load_questions_from_template");
    }
  },

  feedback_form(frm) {
    // When template changes, reload questions into responses
    if (!frm.doc.feedback_form) {
      frm.clear_table("responses");
      frm.refresh_field("responses");
      return;
    }

    frm.trigger("load_questions_from_template");
  },

  refresh(frm) {
    frm.trigger("set_select_options");
  },

  load_questions_from_template(frm) {
    if (!frm.doc.feedback_form) return;

    frappe.db
      .get_doc("Feedback Form", frm.doc.feedback_form)
      .then((template) => {
        frm.clear_table("responses");

        (template.questions || []).forEach((q) => {
          const row = frm.add_child("responses");
          row.question = q.name;
          row.question_label = q.question_label;
          row.question_type = q.question_type;
          row.is_mandatory = q.is_mandatory;
          row.question_options_raw = q.options_raw;
        });

        frm.refresh_field("responses");
        frm.trigger("set_select_options");
      });
  },

  set_select_options(frm) {
    if (!frm.doc.responses) return;
    frm.doc.responses.forEach((row) => {
      if (row.question_type !== "Select" || !row.question) return;

      const grid = frm.get_field("responses").grid;

      for (const row of grid.grid_rows) {
        for (const field of row.docfields) {
          if (field.fieldname === "answer_choice") {
            field.options = [
              "",
              ...row.doc.question_options_raw.split("\n").map((line) => line.trim()).filter((line) => line),
              ]
          }
        }
      }
    });

    frm.refresh_field("responses");
  },
});


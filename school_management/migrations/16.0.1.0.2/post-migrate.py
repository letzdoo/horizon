from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    course_groups = env["school.course_group"].search([])
    for cg in course_groups:
        cg.name = cg.title
        if not cg.ue_id:
            cg.ue_id = "UE-%s" % cg.id

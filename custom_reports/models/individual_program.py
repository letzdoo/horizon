from odoo import fields, models


class IndividualProgramInherit(models.Model):
    _inherit = "school.individual_program"

    is_program_didact = fields.Boolean(
        string="Didactic program",
        help="Indicates whether the program is didactic or not",
    )
    is_bac = fields.Boolean(
        string="Bachelor Program",
        help="Indicates whether the program is a Bachelor or not, in which case is is a master's program. This field is used to determine the diploma report.",
    )

    def return_date_formatted(self, date):
        birth_month = date.strftime("%m")
        birth_month_french = ""
        if birth_month == "01":
            birth_month_french = "janvier"
        elif birth_month == "02":
            birth_month_french = "février"
        elif birth_month == "03":
            birth_month_french = "mars"
        elif birth_month == "04":
            birth_month_french = "avril"
        elif birth_month == "05":
            birth_month_french = "mai"
        elif birth_month == "06":
            birth_month_french = "juin"
        elif birth_month == "07":
            birth_month_french = "juillet"
        elif birth_month == "08":
            birth_month_french = "août"
        elif birth_month == "09":
            birth_month_french = "septembre"
        elif birth_month == "10":
            birth_month_french = "octobre"
        elif birth_month == "11":
            birth_month_french = "novembre"
        elif birth_month == "12":
            birth_month_french = "décembre"
        full_birth_month = (
            date.strftime("%d") + " " + birth_month_french + " " + date.strftime("%Y")
        )
        return full_birth_month

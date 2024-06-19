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
        if not date:
            return "?"
        month = date.strftime("%m")
        month_french = ""
        if month == "01":
            month_french = "janvier"
        elif month == "02":
            month_french = "février"
        elif month == "03":
            month_french = "mars"
        elif month == "04":
            month_french = "avril"
        elif month == "05":
            month_french = "mai"
        elif month == "06":
            month_french = "juin"
        elif month == "07":
            month_french = "juillet"
        elif month == "08":
            month_french = "août"
        elif month == "09":
            month_french = "septembre"
        elif month == "10":
            month_french = "octobre"
        elif month == "11":
            month_french = "novembre"
        elif month == "12":
            month_french = "décembre"
        full_month = (
            date.strftime("%d") + " " + month_french + " " + date.strftime("%Y")
        )
        return full_month

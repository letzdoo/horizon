# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2023 ito-invest.lu
#                       Jerome Sonnet <jerome.sonnet@ito-invest.lu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import json

import pandas as pd
import numpy as np

from odoo import api, fields, models, tools, _
from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

def remove_url_keys(json_data):
    """
    Recursively remove all "url" keys from a nested JSON file.
    :param json_data: JSON data to process.
    :return: Processed JSON data with all "url" keys removed.
    """
    if isinstance(json_data, dict):
        return {k: remove_url_keys(v) for k, v in json_data.items() if k != 'url'}
    elif isinstance(json_data, list):
        return [remove_url_keys(item) for item in json_data]
    else:
        return json_data

class PartnerExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.partner_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Partners")
        for i, obj in enumerate(partners):
            bold = workbook.add_format({"bold": True})
            sheet.write(i, 0, obj.name, bold)
            sheet.write(i, 1, obj.email, bold)
            
class RegistrationExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.registration_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, registrations):
        items = []
        for i, obj in enumerate(registrations):
            item = {
                'id' : obj.id,
                'name' : obj.name,
                'email' : obj.email,
                'contact_form_id' : obj.contact_form_id.id,
                'registration_form_id' : obj.registration_form_id.id,
                'state' : obj.state,
                'kanban_state' : obj.kanban_state,
                'program' : obj.program_id.name,
                'speciality' : obj.speciality_id.name,
            }
            if obj.contact_form_data :
                contact_form_data = json.loads(obj.contact_form_data)
                contact_form_data = remove_url_keys(contact_form_data)
                item['contact_form_data'] = contact_form_data
            if obj.registration_form_data :
                registration_form_data = json.loads(obj.registration_form_data)
                registration_form_data = remove_url_keys(registration_form_data)
                item['registration_form_data'] = registration_form_data
            items.append(item)
        df = pd.json_normalize(items)
        df = df.fillna('').replace([np.inf, -np.inf], '')
        worksheet = workbook.add_worksheet('Registration')
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        for row_num, row_data in enumerate(df.values):
            for col_num, col_data in enumerate(row_data):
                if isinstance(col_data, list):
                    worksheet.write(row_num + 1, col_num, json.dumps(col_data, indent=2))
                else : 
                    worksheet.write(row_num + 1, col_num, col_data)

class ProgramExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.program_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, programs):
        sheet = workbook.add_worksheet("Programs")
        # Write titles
        bold = workbook.add_format({"bold": True})
        sheet.write(0, 0, "id", bold)
        sheet.write(0, 1, "name", bold)
        sheet.write(0, 2, "id_esa", bold)
        sheet.write(0, 3, "cycle", bold)
        sheet.write(0, 4, "admission_criteria_url", bold)
        sheet.write(0, 5, "form_study", bold)
        sheet.write(0, 6, "generic_grade", bold)
        sheet.write(0, 7, "Finalité", bold)
        sheet.write(0, 8, "admission_test_duration", bold)
        sheet.write(0, 9, "academic_year_id", bold)
        sheet.write(0, 10, "program_url", bold)
        sheet.write(0, 11, "Code habilitation", bold)
        sheet.write(0, 12, "Code Etude ARES", bold)
        sheet.write(0, 13, "Code grade académique", bold)
        sheet.write(0, 14, "Année académique de création", bold)
        sheet.write(0, 15, "Horaire", bold)
        sheet.write(0, 16, "Published", bold)
        sheet.write(0, 17, "send_to_hops", bold)
        sheet.write(0, 18, "Dispositif pédagogique", bold)
        sheet.write(0, 19, "Soumis au décret R/RN", bold)
        sheet.write(0, 20, "classification_id", bold)
        sheet.write(0, 21, "status", bold)
        sheet.write(0, 22, "Langue", bold)
        for i, obj in enumerate(programs):
            sheet.write(i, 0, f'gwr.pedagogical.offer_{obj.id}')
            sheet.write(i, 1, obj.name)
            sheet.write(i, 3, "1er cycle" if obj.cycle_id.certification_profile == "bachelor" else "2e cycle")
            sheet.write(i, 6, f"{obj.cycle_id.name} ({obj.cycle_id.ects_required})")
            sheet.write(i, 7, obj.speciality_id.name if obj.speciality_id else ""
            sheet.write(i, 9, obj.year_id.name if obj.academic_year_id else "")
            sheet.write(i, 11, obj.habilitation_code)
            sheet.write(i, 12, obj.ares_code)
            sheet.write(i, 13, obj.graca_code)
            sheet.write(i, 16, False)
            sheet.write(i, 17, False)
            sheet.write(i, 19, False)
            sheet.write(i, 20, f"/ Art / {obj.speciality_id.domain} / {obj.speciality_id.track_id} / {obj.speciality_id.name}" if obj.speciality_id else "")
            sheet.write(i, 21, "Actif")
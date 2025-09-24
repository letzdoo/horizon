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
            sheet.write(i+1, 0, f'gwr.pedagogical.offer_{obj.id}')
            sheet.write(i+1, 1, obj.name)
            sheet.write(i+1, 3, "1er cycle" if obj.cycle_id.certification_profile == "bachelor" else "2e cycle")
            sheet.write(i+1, 6, f"{obj.cycle_id.name} ({obj.cycle_id.required_credits})")
            sheet.write(i+1, 7, obj.speciality_id.name if obj.speciality_id else "")
            sheet.write(i+1, 9, obj.year_id.name if obj.year_id else "")
            sheet.write(i+1, 11, obj.habilitation_code)
            sheet.write(i+1, 12, obj.ares_code)
            sheet.write(i+1, 13, obj.graca_code)
            sheet.write(i+1, 16, False)
            sheet.write(i+1, 17, False)
            sheet.write(i+1, 19, False)
            sheet.write(i+1, 20, f"/ Art / {obj.speciality_id.domain_id.name} / {obj.speciality_id.track_id} / {obj.speciality_id.name}" if obj.speciality_id else "")
            sheet.write(i+1, 21, "Actif")

class BlockExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.bloc_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"
    
    def generate_xlsx_report(self, workbook, data, blocs):
        sheet = workbook.add_worksheet("Blocks")
        # Write titles
        bold = workbook.add_format({"bold": True})
        sheet.write(0, 0, "ID externe", bold)
        sheet.write(0, 1, "Année académique", bold)
        sheet.write(0, 2, "Bloc", bold)
        sheet.write(0, 3, "Offres pédagogiques", bold)
        sheet.write(0, 4, "ID de l'offre pédagogique", bold)
        sheet.write(0, 5, "Établissement", bold)
        for i, obj in enumerate(blocs):
            sheet.write(i+1, 0, f'gwr.pedagogical.block_{obj.id}')
            sheet.write(i+1, 1, obj.year_id.name if obj.year_id else "")
            sheet.write(i+1, 2, f"Block {obj.sequence}")
            sheet.write(i+1, 3, obj.program_id.name if obj.program_id else "")
            sheet.write(i+1, 4, f"gwr.pedagogical.offer_{obj.program_id.id}" if obj.program_id else "")
            sheet.write(i+1, 5, "Conservatoire royal de Liège")

class TeacherExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.teacher_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"

    #ID externe	Enseignant	Nom de famille	Prénom	Téléphone 1	Téléphone 2	Email personnel	E-mail	
    #Genre	Matricule Enseignant / Administrateur ESA	national_registration_number	Date de naissance	
    # Pays de naissance	Langue	Société	Etablissements
    
    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Teachers")

        # Write titles
        bold = workbook.add_format({"bold": True})
        sheet.write(0, 0, "ID externe", bold)
        sheet.write(0, 1, "Enseignant", bold)
        sheet.write(0, 2, "Nom de famille", bold)
        sheet.write(0, 3, "Prénom", bold)
        sheet.write(0, 4, "Téléphone 1", bold)
        sheet.write(0, 5, "Téléphone 2", bold)
        sheet.write(0, 6, "Email personnel", bold)
        sheet.write(0, 7, "E-mail", bold)
        sheet.write(0, 8, "Genre", bold)
        sheet.write(0, 9, "Matricule Enseignant / Administrateur ESA", bold)
        sheet.write(0, 10, "national_registration_number", bold)
        sheet.write(0, 11, "Date de naissance", bold)
        sheet.write(0, 12, "Pays de naissance", bold)
        sheet.write(0, 13, "Langue", bold)
        sheet.write(0, 14, "Société", bold)
        sheet.write(0, 15, "Etablissements", bold)
        for i, obj in enumerate(partners):
            sheet.write(i+1, 0, f'res_partner_teacher_WBE_{obj.id}')
            sheet.write(i+1, 1, "TRUE")
            sheet.write(i+1, 2, obj.lastname if obj.lastname else "")
            sheet.write(i+1, 3, obj.firstname if obj.firstname else "")
            sheet.write(i+1, 4, obj.phone if obj.phone else "")
            sheet.write(i+1, 5, obj.mobile if obj.mobile else "")
            sheet.write(i+1, 6, obj.email_personnel if obj.email_personnel else "")
            sheet.write(i+1, 7, obj.email if obj.email else "")
            sheet.write(i+1, 8, "M" if obj.gender == "male" else "F")
            sheet.write(i+1, 9, obj.mat_number if obj.mat_number else "")
            sheet.write(i+1, 10, obj.reg_number if obj.reg_number else "")
            sheet.write(i+1, 11, fields.Date.to_string(obj.birthdate_date) if obj.birthdate_date else "")
            sheet.write(i+1, 12, obj.birthcountry.name if obj.birthcountry else "")
            sheet.write(i+1, 13, obj.lang if obj.lang else "")
            sheet.write(i+1, 14, "Conservatoire royal de Liège")
            sheet.write(i+1, 15, "Conservatoire royal de Liège")

class StudentExportXlsx(models.AbstractModel):
    _name = "report.school_reporting_xlsx.student_export_xlsx"
    _description = "Report xlsx helpers"
    _inherit = "report.report_xlsx.abstract"

    #ID Etudiant	Etudiant? 	Etablissement	Etablissements	Nom de famille	
    # Prénom	Nom d'usage 	Prénom d'usage	Matricule Etudiant	Email 	
    # Email personnel	Téléphone 1	Téléphone 2	Rue	Numéro 	Ville	Code postal	Pays	
    # Rue Secondaire	Ville secondaire	Numéro rue secondaire	Code postal secondaire	
    # Pays secondaire	Date de naissance 	Pays de naissance	Nationalité	Statut national spécial	
    # Numéro de registre national ou RN Bis	Genre	Pronom d'usage 	Décès de l'étudiant	
    # Deuxième prénom 	Autre prénom	HUE?	Prénom contact d'urgence	Nom contact d'urgence	
    # Téléphone contact d'urgence	Mail contact d'urgence	Prénom responsable légal	
    # Nom responsable légal	Téléphone responsable légal	Email responsable légal
    
    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Students")

        # Write titles
        bold = workbook.add_format({"bold": True})
        sheet.write(0, 0, "ID Etudiant", bold)
        sheet.write(0, 1, "Etudiant?", bold)
        sheet.write(0, 2, "Etablissement", bold)
        sheet.write(0, 3, "Etablissements", bold)
        sheet.write(0, 4, "Nom de famille", bold)
        sheet.write(0, 5, "Prénom", bold)
        sheet.write(0, 6, "Nom d'usage", bold)
        sheet.write(0, 7, "Prénom d'usage", bold)
        sheet.write(0, 8, "Matricule Etudiant", bold)
        sheet.write(0, 9, "Email", bold)
        sheet.write(0, 10, "Email personnel", bold)
        sheet.write(0, 11, "Téléphone 1", bold)
        sheet.write(0, 12, "Téléphone 2", bold)
        sheet.write(0, 13, "Rue", bold)
        sheet.write(0, 14, "Numéro", bold)
        sheet.write(0, 15, "Ville", bold)
        sheet.write(0, 16, "Code postal", bold)
        sheet.write(0, 17, "Pays", bold)
        sheet.write(0, 18, "Rue Secondaire", bold)
        sheet.write(0, 19, "Ville secondaire", bold)
        sheet.write(0, 20, "Numéro rue secondaire", bold)
        sheet.write(0, 21, "Code postal secondaire", bold)
        sheet.write(0, 22, "Pays secondaire", bold)
        sheet.write(0, 23, "Date de naissance", bold)
        sheet.write(0, 24, "Pays de naissance", bold)
        sheet.write(0, 25, "Nationalité", bold)
        sheet.write(0, 26, "Statut national spécial", bold)
        sheet.write(0, 27, "Numéro de registre national ou RN Bis", bold)
        sheet.write(0, 28, "Genre", bold)
        sheet.write(0, 29, "Pronom d'usage", bold)
        sheet.write(0, 30, "Décès de l'étudiant", bold)
        sheet.write(0, 31, "Deuxième prénom", bold)
        sheet.write(0, 32, "Autre prénom", bold)
        sheet.write(0, 33, "HUE?", bold)
        sheet.write(0, 34, "Prénom contact d'urgence", bold)
        sheet.write(0, 35, "Nom contact d'urgence", bold)
        sheet.write(0, 36, "Téléphone contact d'urgence", bold)
        sheet.write(0, 37, "Mail contact d'urgence", bold)
        sheet.write(0, 38, "Prénom responsable légal", bold)
        sheet.write(0, 39, "Nom responsable légal", bold)
        sheet.write(0, 40, "Téléphone responsable légal", bold)
        sheet.write(0, 41, "Email responsable légal", bold)
        
        for i, obj in enumerate(partners):
            sheet.write(i+1, 0, f'res_partner_student_ESA_{obj.id}')
            sheet.write(i+1, 1, "TRUE")
            sheet.write(i+1, 2, "Conservatoire royal de Liège")
            sheet.write(i+1, 3, "Conservatoire royal de Liège")
            sheet.write(i+1, 4, obj.lastname if obj.lastname else "")
            sheet.write(i+1, 5, obj.firstname if obj.firstname else "")
            sheet.write(i+1, 6, obj.lastname if obj.lastname else "")
            sheet.write(i+1, 7, obj.firstname if obj.firstname else "")
            sheet.write(i+1, 8, obj.mat_number if obj.mat_number else "")
            sheet.write(i+1, 9, obj.email if obj.email else "")
            sheet.write(i+1, 10, obj.email_personnel if obj.email_personnel else "")
            sheet.write(i+1, 11, obj.phone if obj.phone else "")
            sheet.write(i+1, 12, obj.mobile if obj.mobile else "")
            sheet.write(i+1, 13, obj.street if obj.street else "")
            sheet.write(i+1, 14, "")
            sheet.write(i+1, 15, obj.city if obj.city else "")
            sheet.write(i+1, 16, obj.zip if obj.zip else "")
            sheet.write(i+1, 17, obj.country_id.name if obj.country_id else "")
            sheet.write(i+1, 18, obj.secondary_street if obj.secondary_street else "")
            sheet.write(i+1, 19, obj.secondary_city if obj.secondary_city else "")
            sheet.write(i+1, 20, "")
            sheet.write(i+1, 21, obj.secondary_zip if obj.secondary_zip else "")
            sheet.write(i+1, 22, obj.secondary_country_id.name if obj.secondary_country_id else "")
            sheet.write(i+1, 23, fields.Date.to_string(obj.birthdate_date) if obj.birthdate_date else "")
            sheet.write(i+1, 24, obj.birthcountry.name if obj.birthcountry else "")
            nationalities = obj.nationality_ids.mapped('name')
            sheet.write(i+1, 25, ", ".join(nationalities) if nationalities else "")
            sheet.write(i+1, 26, "Indéterminée")
            sheet.write(i+1, 27, obj.reg_number if obj.reg_number else "")
            sheet.write(i+1, 28, "M" if obj.gender == "male" else "F")
            sheet.write(i+1, 29, "")
            sheet.write(i+1, 30, "FALSE")
            sheet.write(i+1, 31, "")
            sheet.write(i+1, 32, "")
            sheet.write(i+1, 33, "FALSE")
            # Rest we don't have the data for now

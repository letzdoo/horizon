import json
import logging

from odoo import http
from odoo.http import Response, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

class WebsiteSchoolPortal(CustomerPortal):
    # Route appelée lors de la soumission du formulaire de génération d'un document
    @route(['/my/generate-document'], type='json', auth="user", website=True)
    def generate_document(self, **kw):
        document_to_generate = kw.get("document_to_generate")
        if document_to_generate:
            array = document_to_generate.split(":")
            if (len(array) == 2):
                partner_id = request.env.user.partner_id.id
                # partner_id = 10218
                report_action = array[0]
                res_id_report = array[1]
                report = request.env.ref(report_action).sudo()

                # Est-ce que le rapport est déjà disponible sur google drive ?
                searchParams = [
                    ('res_id', '=', partner_id),
                    ('res_model_report', '=', report.model),
                    ('res_id_report', '=', int(res_id_report)),
                    ('report_id', '=', report.id)
                ]
                order = 'create_date DESC'
                google_doc = request.env['google_drive_file'].sudo().search(searchParams, limit=1, order=order)
                if (google_doc):
                    # Affichage
                    return {"result": "success",
                            "existing": True,
                            "documentlink" : "/google_documents/view_file/" + google_doc.googe_drive_id}
                
                # Sinon, génération du document
                try:
                    report.sudo()._render_qweb_pdf(report_action, [int(res_id_report)])[0]
                    searchParams = [
                        ('res_id', '=', partner_id),
                        ('res_model_report', '=', report.model),
                        ('res_id_report', '=', int(res_id_report)),
                        ('report_id', '=', report.id)
                    ]
                    order = 'create_date DESC'
                    google_doc = request.env['google_drive_file'].sudo().search(searchParams, limit=1, order=order)
                    if google_doc:
                        # Affichage
                        return {"result": "success",
                                "existing": False,
                                "documentlink" : "/google_documents/view_file/" + google_doc.googe_drive_id}
                except:
                    _logger.error("generate_document() : an error occured while generating the document.")
                    _logger.exception("..")
                    return {"result": "failure"}

        return {"result": "failure"}
    
    # Héritage, prépare les données à afficher dans le portail
    def _prepare_portal_layout_values(self, **kw):
        # Récupération des valeurs de base
        values = super(WebsiteSchoolPortal, self)._prepare_portal_layout_values()

        # Liste des documents existants et des documents à générer
        google_docs, docs_to_generate = self.get_all_documents(request.env.user.partner_id.id)
        # google_docs, docs_to_generate = self.get_all_documents(10218)

        values['google_docs'] = google_docs
        values['docs_to_generate'] = docs_to_generate
        return values
    
    # Récupère les ids nécessaires à la création d'un rapport
    def _get_report_objects(self, student_id, model, optional_params = []):
        searchParams = [
            ('state', '!=', 'draft'),
            ('student_id', '=', student_id)
        ]
        # Ajout de paramètres de recherche optionnels
        searchParams += optional_params
        result = request.env[model].sudo().search(searchParams)
        return result
    
    # Fonction générique récupérant les documents à montrer et les documents à générer pour un rapport donné.
    def _get_docs(self, student_id, res_model, report_code, report_id, label, can_generate = True, optional_params_to_show = [], optional_params_to_generate = []):
        docs_to_show = []
        docs_to_generate = []

        # Lecture des google docs existants pour le rapport.
        searchParams = [
            ('res_id', '=', student_id),
            ('res_model_report', '=', res_model),
            ('res_id_report', '!=', None),
            ('report_id', '=', report_id),
        ] 
        order = 'create_date DESC'
        existing_docs = request.env['google_drive_file'].sudo().search(searchParams, order=order)

        #######################################
        ### GESTION DES DOCUMENTS À MONTRER ###
        #######################################

        # Lecture des objets métiers pour lesquels les document éventuels peuvent être montrés.
        to_show = self._get_report_objects(student_id, res_model, optional_params_to_show)
        # Boucle sur les documents existants pour ne reprendre que ceux qui sont à montrer.
        for doc in existing_docs:
            if  next((True for object in to_show if object.id == doc.res_id_report), False):
                doc.label = label
                docs_to_show.append(doc)

        #######################################
        ### GESTION DES DOCUMENTS À GÉNÉRER ###
        #######################################

        if can_generate:
            # Lecture des objets métiers pour lesquels les document éventuels peuvent être générés.
            to_generate = self._get_report_objects(student_id, res_model, optional_params_to_generate)

            # Boucle sur les documents pouvant être générés en ne reprenant que ceux qui n'existent pas déjà.
            for object in to_generate:
                if next((False for doc in existing_docs if object.id == doc.res_id_report), True):
                    docs_to_generate.append({
                        "code": report_code+':'+str(object.id),
                        "label": label + " : "+ object.name + " - " + (object.source_program_id.name if res_model == 'school.individual_program' else object.source_bloc_title),
                    })

        return docs_to_show, docs_to_generate

    # Renvoie une liste des documents qui peuvent être générés
    def get_all_documents(self, student_id):

        docs_to_show = []
        docs_to_generate = []

        ###########################
        # Attestation de réussite #
        ###########################
        report_code = 'school_evaluations.report_success_certificate_prog'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_program'
            optional_params_to_show = [('name','not like','XXX')] # Exemple de critère d'exclusion pour les documents montrés.
            optional_params_to_generate = [('name','not like','XXX')] # Exemple de critère d'exclusion pour les documents à générer.
            label = "Attestation de réussite"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, True, optional_params_to_show, optional_params_to_generate)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        ################################
        # Attestation de fréquentation #
        ################################
        report_code = 'school_management.report_attendance_for_student'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_bloc'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "Attestation de fréquentation"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, True, optional_params_to_show, optional_params_to_generate)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        ###################
        # Aperçu du cycle #
        ###################
        report_code = 'school_evaluations.report_individual_bloc_definition'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_program'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "Aperçu du cycle"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, True, optional_params_to_show, optional_params_to_generate)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        ####################
        # Imprimer Diplôme #
        ####################
        report_code = 'custom_reports.report_school_general_diploma_report'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_program'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "Diplôme"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, False, optional_params_to_show)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate
        
        #######################
        # Imprimer Supplément #
        #######################
        report_code = 'custom_reports.report_school_individual_program_supplement_general'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_program'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "Supplément au diplôme"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, False, optional_params_to_show)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        ########################################
        # PAE (Programme Annuel de l'Etudiant) #
        ########################################
        report_code = 'school_management.report_individual_bloc'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_bloc'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "PAE (Programme Annuel de l'Etudiant)"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, True, optional_params_to_show, optional_params_to_generate)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        ###########################
        # Rapport de délibération #
        ###########################
        report_code = 'school_evaluations.report_deliberation_annexe'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_bloc'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "Rapport de délibération"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, False, optional_params_to_show)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        ###################
        # Relevé de notes #
        ###################
        report_code = 'school_evaluations.report_evaluation_for_student'
        report = request.env.ref(report_code).sudo()
        if report.google_drive_enabled and report.google_drive_patner_field:
            res_model = 'school.individual_bloc'
            optional_params_to_show = [] # TODO.
            optional_params_to_generate = [] # TODO.
            label = "Relevé de notes"

            to_show, to_generate = self._get_docs(student_id, res_model, report_code, report.id, label, True, optional_params_to_show, optional_params_to_generate)

            if len(to_show) > 0:
                docs_to_show += to_show
            if len(to_generate) > 0:
                docs_to_generate += to_generate

        return docs_to_show, docs_to_generate 
                
        
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

import json
import logging

import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools import ustr

from odoo.addons.http_routing.models.ir_http import unslug
from odoo.addons.web.controllers.main import CSVExport

_logger = logging.getLogger(__name__)


class csv_school_management(CSVExport):
    @http.route("/web/export/course", type="http", auth="user")
    # @serialize_exception
    def export_course(self):
        data = """{
          "model": "school.course",
          "fields": [
            {
              "name": "id",
              "label": "External ID"
            },
            {
              "name": "domain_name",
              "label": "Domaine/Identifiant"
            },
            {
              "name": "teacher_ids/id",
              "label": "Enseignants/Identifiant"
            },
            {
              "name": "credits",
              "label": "ECTS"
            },
            {
              "name": ".id",
              "label": "Identifiant"
            },
            {
              "name": "level",
              "label": "Niveau"
            },
            {
              "name": "name",
              "label": "Nom"
            },
            {
              "name": "weight",
              "label": "Poids"
            },
            {
              "name": "has_second_session",
              "label": "Seconde session possible"
            },
            {
              "name": "section_id/id",
              "label": "Section/Identifiant"
            },
            {
              "name": "speciality_id/id",
              "label": "Spécialité/Identifiant"
            },
            {
              "name": "type",
              "label": "Type"
            },
            {
              "name": "url_ref",
              "label": "Url Reference"
            },
            {
              "name": "course_group_id/id",
              "label": "Unité d'enseignement/Identifiant"
            },
            {
              "name": "hours",
              "label": "Heures"
            }
          ],
          "ids": false,
          "domain": [],
          "context": {
            "lang": "fr_BE",
            "tz": "Europe/Brussels",
            "uid": 1,
            "params": {
              "action": 126
            }
          },
          "import_compat": true
        }"""
        return self.base(data, "1551704801155")

    @http.route("/web/export/course_group", type="http", auth="user")
    # @serialize_exception
    def export_course_group(self):
        data = """{
                  "model": "school.course_group",
                  "fields": [
                    {
                      "name": "id",
                      "label": "External ID"
                    },
                    {
                      "name": "bloc_ids/id",
                      "label": "Blocs annuels/Identifiant"
                    },
                    {
                      "name": "co_requisit_ids/.id",
                      "label": "Corequis/Identifiant"
                    },
                    {
                      "name": "create_date",
                      "label": "Créé le"
                    },
                    {
                      "name": "domain_name",
                      "label": "Domaine/Nom"
                    },
                    {
                      "name": ".id",
                      "label": "Identifiant"
                    },
                    {
                      "name": "teacher_id/teacher",
                      "label": "Enseignant/Enseignant"
                    },
                    {
                      "name": "teacher_id/display_name",
                      "label": "Enseignant/Nom"
                    },
                    {
                      "name": "teacher_id/name",
                      "label": "Enseignant/Nom"
                    },
                    {
                      "name": "name",
                      "label": "Nom"
                    },
                    {
                      "name": "weight",
                      "label": "Poids"
                    },
                    {
                      "name": "pre_requisit_course_ids/id",
                      "label": "Prérequis/Identifiant"
                    },
                    {
                      "name": "pre_requisit_ids/id",
                      "label": "Prérequis/Identifiant"
                    },
                    {
                      "name": "title",
                      "label": "Titre"
                    },
                    {
                      "name": "total_weight",
                      "label": "Total de la pondération"
                    },
                    {
                      "name": "total_credits",
                      "label": "Total des ECTS"
                    },
                    {
                      "name": "total_hours",
                      "label": "Total des Heures"
                    },
                    {
                      "name": "period",
                      "label": "Période"
                    }
                  ],
                  "ids": false,
                  "domain": [],
                  "context": {
                    "lang": "fr_BE",
                    "tz": "Europe/Brussels",
                    "uid": 1,
                    "params": {
                      "action": 108
                    }
                  },
                  "import_compat": true
                }"""
        return self.base(data, "1551704801155")

    @http.route("/web/export/bloc", type="http", auth="user")
    # @serialize_exception
    def export_blocs(self):
        data = """{
                  "model": "school.bloc",
                  "fields": [
                    {
                      "name": "id",
                      "label": "External ID"
                    },
                    {
                      "name": "year_id/name",
                      "label": "Année scolaire/Nom"
                    },
                    {
                      "name": "domain_name",
                      "label": "Domaine/Nom"
                    },
                    {
                      "name": "name",
                      "label": "Nom"
                    },
                    {
                      "name": "level",
                      "label": "Niveau"
                    },
                    {
                      "name": "track_id/name",
                      "label": "Option/Nom"
                    },
                    {
                      "name": "track_id/saturn_code",
                      "label": "Option/Saturn Code"
                    },
                    {
                      "name": "total_credits",
                      "label": "Total des ECTS"
                    },
                    {
                      "name": "total_weight",
                      "label": "Total de la pondération"
                    },
                    {
                      "name": "total_hours",
                      "label": "Total des Heures"
                    },
                    {
                      "name": "program_id/id",
                      "label": "Programme/Identifiant"
                    }
                  ],
                  "ids": false,
                  "domain": [
                    [
                      "year_sequence",
                      "=",
                      "current"
                    ],
                    [
                      "title",
                      "ilike",
                      "master"
                    ]
                  ],
                  "context": {
                    "lang": "fr_BE",
                    "tz": "Europe/Brussels",
                    "uid": 1,
                    "params": {
                      "action": 109
                    }
                  },
                  "import_compat": true
                }"""
        return self.base(data, "1551704801155")

    @http.route("/web/export/program", type="http", auth="user")
    # @serialize_exception
    def export_programs(self):
        data = """{
            "model": "school.program",
            "fields": [
              {
                "name": "id",
                "label": "External ID"
              },
              {
                "name": "year_id/id",
                "label": "Année scolaire/Identifiant"
              },
              {
                "name": "year_id/name",
                "label": "Année scolaire/Nom"
              },
              {
                "name": "create_date",
                "label": "Créé le"
              },
              {
                "name": "create_uid/id",
                "label": "Créé par/Identifiant"
              },
              {
                "name": "write_uid/id",
                "label": "Dernière mise à jour par/Identifiant"
              },
              {
                "name": "__last_update",
                "label": "Dernière modification le"
              },
              {
                "name": "domain_name",
                "label": "Domaine/Nom"
              },
              {
                "name": "name",
                "label": "Nom"
              },
              {
                "name": "track_id/id",
                "label": "Option/Identifiant"
              },
              {
                "name": "track_id/name",
                "label": "Option/Nom"
              },
              {
                "name": "section_id/id",
                "label": "Section/Identifiant"
              },
              {
                "name": "section_id/name",
                "label": "Section/Nom"
              },
              {
                "name": "speciality_id/id",
                "label": "Spécialité/Identifiant"
              },
              {
                "name": "speciality_id/name",
                "label": "Spécialité/Nom"
              },
              {
                "name": "state",
                "label": "État"
              },
              {
                "name": "total_credits",
                "label": "Total des ECTS"
              },
              {
                "name": "total_hours",
                "label": "Total des Heures"
              }
            ],
            "ids": false,
            "domain": [
              [
                "year_sequence",
                "=",
                "current"
              ]
            ],
            "context": {
              "lang": "fr_BE",
              "tz": "Europe/Brussels",
              "uid": 1,
              "search_default_current": 1,
              "params": {
                "action": 110
              }
            },
            "import_compat": true
          }"""
        return self.base(data, "1551704801155")


class website_portal_school_management(http.Controller):
    @http.route(["/program_json/<program_id>"], type="http", auth="public")
    def program_details_json(self, program_id, redirect=None, **post):
        _, program_id = unslug(program_id)
        program = (
            request.env["school.program"].sudo().search_read([("id", "=", program_id)])
        )
        if program:
            program = program[0]
            program.pop("course_group_ids")
            blocs = (
                request.env["school.bloc"]
                .sudo()
                .search_read([("id", "in", program["bloc_ids"])])
            )
            for bloc in blocs:
                bloc["cycle_id"] = (
                    request.env["school.cycle"]
                    .sudo()
                    .search_read([("id", "=", bloc["cycle_id"][0])])
                )
                bloc["speciality_id"] = (
                    request.env["school.speciality"]
                    .sudo()
                    .search_read([("id", "=", bloc["speciality_id"][0])])
                )
                course_groups = (
                    request.env["school.course_group"]
                    .sudo()
                    .search_read([("id", "in", bloc["course_group_ids"])])
                )
                for cg in course_groups:
                    cg.pop("bloc_ids")
                    courses = (
                        request.env["school.course"]
                        .sudo()
                        .search_read([("id", "in", cg["course_ids"])])
                    )
                    for c in courses:
                        c.pop("bloc_ids")
                    cg["course_ids"] = courses
                bloc["course_group_ids"] = course_groups
            program["bloc_ids"] = blocs
            body = json.dumps(program, default=ustr)
            response = request.make_response(
                body,
                [
                    # this method must specify a content-type application/json instead of using the default text/html set because
                    # the type of the route is set to HTTP, but the rpc is made with a get and expects JSON
                    ("Content-Type", "application/json"),
                    ("Cache-Control", "public, max-age=" + str(http.STATIC_CACHE_LONG)),
                ],
            )
            return response
        else:
            raise werkzeug.exceptions.HTTPException(description="Unkown program.")

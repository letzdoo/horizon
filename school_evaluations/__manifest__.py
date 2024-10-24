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
{
    "name": "School evaluations",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ito-invest (Jerome Sonnet)",
    "website": "https://github.com/ito-invest-lu/horizon",
    "category": "School Management",
    "depends": [
        "school_management",
        "google_documents",
    ],
    "init_xml": [],
    "data": [
        "data/school_evaluations.xml",
        "views/evaluation_view.xml",
        "views/configuration_view.xml",
        "views/ir_ui_menu.xml",
        "report/report_evaluation.xml",
        "wizard/evaluation_summary.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "school_evaluations/static/src/css/school_evaluations.css"
        ]
    },
    "demo_xml": [],
    "qweb": ["static/src/xml/*.xml"],
    "installable": True,
    "application": True,
}

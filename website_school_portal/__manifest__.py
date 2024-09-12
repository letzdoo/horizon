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
    "name": "Website School Portal",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "Neodiensis,ito-invest (Jerome Sonnet)",
    "website": "https://github.com/ito-invest-lu/horizon",
    "category": "School Management",
    "depends": [
        "web",
        "website",
        "website_school_management",
        "website_booking",
        "google_documents",
    ],
    "data": [
        "init_horizon.xml",
        "views/main.xml",
        "views/footer.xml",
        "views/header.xml",
        "views/custom.xml",
        "views/snippets.xml",
        "views/page_404.xml",
        "views/page_403.xml",
        "views/mes_donnees.xml",
        "views/reservations.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_school_portal/static/src/js/snippet.js",
            "website_school_portal/static/src/js/generate-doc.js",
            "website_school_portal/static/src/scss/main.scss",
        ]
    },
    "installable": True,
    "application": True,
    "images": [
        "static/description/icon.png",
    ],
}

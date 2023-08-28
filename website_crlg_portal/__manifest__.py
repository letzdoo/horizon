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
    "name": "Website CRLG Portal",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "Neodiensis,ito-invest (Jerome Sonnet)",
    "website": "https://github.com/ito-invest-lu/horizon",
    "category": "School Management",
    "depends": ["website_school_portal"],
    "data": [
        "init_crlg.xml",
        "views/footer.xml",
        "views/custom.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "website_crlg_portal/static/src/scss/variables.scss",
        ],
        "web.assets_frontend": [
            "website_crlg_portal/static/src/scss/main.scss",
        ],
    },
    "installable": True,
    "application": True,
    "images": [
        "static/description/icon.png",
    ],
}

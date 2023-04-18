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
{
    'name': 'School valuations',
    'version': '0.1',
    'license': 'AGPL-3',
    'author': 'ito-invest (Jerome Sonnet)',
    'website': '',
    'category': 'School Management',
    'depends': ['school_evaluations'],
    'init_xml': [],
    'data': [
        'valuations_data.xml',
        'views/valuations_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'description': '''
        This modules manage valuations of course groups.
    ''',
    'active': False,
    'installable': True,
    'application': True,
}

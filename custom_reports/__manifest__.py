# -*- coding: utf-8 -*-
{
    "name": "Custom Reports",
    "summary": """This module adds custom reports that canbe printed""",
    "author": "Deuse",
    "website": "https://github.com/ito-invest-lu/horizon",
    "version": "16.0.1.0.1",
    "depends": [
        "school_management",
        "base",
        "partner_contact_gender",
        "partner_contact_birthdate",
        "partner_firstname",
        "custom_partner_fields",
    ],
    "data": [
        "templates/layouts/diploma_layout.xml",
        "templates/layouts/supplement_layout.xml",
        "templates/paperformats/diploma_paperformat.xml",
        "templates/paperformats/supplement_paperformat.xml",
        "templates/school_individual_program_diploma.xml",
        "templates/school_individual_program_supplement.xml",
        "views/individual_program_view.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "license": "LGPL-3",
}

# -*- coding: utf-8 -*-

from odoo import fields, models


class Erasmus(models.Model):
    _name = "custom_partner_fields.erasmus"
    _description = "Erasmus"

    establishment = fields.Char(string="Etablissement")
    city = fields.Char(string="Ville")
    country = fields.Char(string="Pays")

    start_date = fields.Date(string="Date de début")
    end_date = fields.Date(string="Date de fin")

    language = fields.Char(string="Langue")

    partner_id = fields.Many2one("res.partner", string="Contact")


class Internship(models.Model):
    _name = "custom_partner_fields.internship"
    _description = "Internship"

    establishment = fields.Char(string="Etablissement")
    city = fields.Char(string="Ville")
    country = fields.Char(string="Pays")

    start_date = fields.Date(string="Date de début")
    end_date = fields.Date(string="Date de fin")

    partner_id = fields.Many2one("res.partner", string="Contact")


class MemoirTitle(models.Model):
    _name = "custom_partner_fields.memoir_title"
    _description = "Memoir Title"

    name = fields.Char(string="Titre du mémoire/TFE")
    partner_id = fields.Many2one("res.partner", string="Contact")


class TitleAccess(models.Model):
    _name = "custom_partner_fields.access_title"
    _description = "Title Access"

    name = fields.Char(
        string="Name of the access title",
        help="e.g.: Titre d'accés 1er cycle (art. 107)",
    )
    title = fields.Char(string="Intitulé")
    establishment = fields.Char(string="Etablissement")
    city = fields.Char(string="Ville")
    country = fields.Char(string="Pays")
    date = fields.Date(string="Date")

    partner_id = fields.Many2one("res.partner", string="Contact")


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    second_first_name = fields.Char(string="Autre(s) prénom(s)")

    # Section Titre d'acces
    admission_exam_date = fields.Date(string="Examen d'admission")
    access_titles_ids = fields.One2many(
        "custom_partner_fields.access_title", "partner_id", string="Titres d'accés"
    )
    memoir_titles_ids = fields.One2many(
        "custom_partner_fields.memoir_title", "partner_id", string="Titres de mémoires"
    )
    internships_ids = fields.One2many(
        "custom_partner_fields.internship", "partner_id", string="Stage(s)"
    )
    erasmus_ids = fields.One2many(
        "custom_partner_fields.erasmus", "partner_id", string="Erasmus"
    )

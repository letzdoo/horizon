# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
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

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class SchoolSaturnStatistics(models.Model):
    _name = 'school.saturn'

    _inherit = ['mail.thread','school.year_sequence.mixin']

    name = fields.Char(compute="_compute_name")
    
    @api.one
    @api.depends('year_id')
    def _compute_name(self):
        self.name = "Collecte Saturn %s" % self.year_id.name

    state = fields.Selection([
            ('draft','Draft'),
            ('validated', 'Validated')
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange',
        copy=False,
        help=" * The 'Draft' status is used when a new statistic file is created and not validated yet.\n"
             " * The 'Validated' status is when a statistic file is validated and available for use.")

    @api.multi
    def draft(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def validate(self):
        return self.write({'state': 'validated'})

    year_id = fields.Many2one('school.year', string='Year', required=True, default=lambda self: self.env.user.current_year_id)
    bloc_ids = fields.Many2many('school.individual_bloc', 'school_saturn_bloc_rel', 'saturn_id', 'individual_bloc_id', string='Individual Blocs', domain="[('year_id','=',year_id)]")

    bloc_count = fields.Integer(string="Bloc Count", compute="_compute_count")
    student_count = fields.Integer(string="Student Count", compute="_compute_count")

    @api.one
    @api.depends('bloc_ids')
    def _compute_count(self):
        self.bloc_count = len(self.bloc_ids)
        self.student_count = len(set(self.bloc_ids.mapped('student_id')))
        
class Etablissement(models.Model):
    '''Etablissement'''
    _name = 'school.stat_etablissement'
    
    name = fields.Char(string="Name")
    code_fase = fields.Char(string="Code FASE")
    
class Domaine(models.Model):
    '''Domaine'''
    _name = 'school.stat_domain'
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")

class Partner(models.Model):
    '''Partner'''
    _inherit = 'res.partner'

    student_historic_entry_ids = fields.One2many('school.student_history_entry', 'student_id', string="Student History Entries", track_visibility='onchange')
    birthcountry = fields.Many2one('res.country', string='Birthcountry')

    mobility = fields.Selection([('0','Non'),('1','Mobilité européenne'),('2','Mobilité non-européenne')], description='Fields C5',string='Mobilité', default='0', required=True)
    generation = fields.Selection([('1','Non'),('2','Oui, en FWB ou en Communauté germanophone'),('3','Oui, en Communauté flamande'),('4','Oui, à l’étranger')],description='Fields C14',string='Première génération', default='1', required=True)
    mob_type = fields.Selection([('AC','Mobilité académique'),('ST','Mobilité de stage'),('NA','Non applicable')],description='Fields C19',string='Type de mobilité',default='NA', required=True)
    modeste = fields.Selection([('0','Conditions normales'),('1','Conditions modestes')],description='Fields D8',string='Etudiant de condition modeste',default=0)

class StudentHistoryEntry(models.Model):
    '''Student History Entry'''
    _name = 'school.student_history_entry'
    
    year_id = fields.Many2one('school.year', string="Year", required=True)
    student_id = fields.Many2one('res.partner', string="Student", required=True)
    activite = fields.Selection([
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], string="Activité", required=True)
    etablissement_id = fields.Many2one('school.stat_etablissement', string="Etablissement", required=True)
    domain_id = fields.Many2one('school.stat_domain', string="Domaine", required=True)
    annee = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], string="Année", required=True)
    resultat = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ],string="Résultat", required=True)

class Domain(models.Model):
    '''Domain'''
    _inherit = 'school.domain'

    saturn_code = fields.Char(string="Saturn Code")

class Section(models.Model):
    '''Section'''
    _inherit = 'school.section'

    saturn_code = fields.Char(string="Saturn Code")

class Track(models.Model):
    '''Track'''
    _inherit = 'school.track'

    saturn_code = fields.Char(string="Saturn Code")

class Speciality(models.Model):
    '''Speciality'''
    _inherit = 'school.speciality'

    saturn_code = fields.Char(string="Saturn Code")
    
class Cycle(models.Model):
    '''Speciality'''
    _inherit = 'school.cycle'

    saturn_code = fields.Char(string="Saturn Code")
    type_second_cycle = fields.Selection([('A','Approfondie'),('D','Didactique'),('S','Specialisée')],string='Finalité du 2e cycle')
    is_jeune_talent = fields.Boolean(string='Jeunes Talents (Musique)')
    
class Company(models.Model):
    _inherit = 'res.company'
    
    code_fase = fields.Char(string="Code Fase de l''Ecole supérieure des Arts")
    
class IndividualBloc(models.Model):
    _inherit = 'school.individual_bloc'
    
    is_saturn_validated = fields.Boolean(string="Validated for Saturn")
    
    company_currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id')
    
    student_historic_entry_ids = fields.One2many('school.student_history_entry', related='student_id.student_historic_entry_ids')
    
    field_a1 = fields.Char(description='Fields A1',string='Code Fase de l''Ecole supérieure des Arts', default=lambda self: self.env.user.company_id.code_fase,readonly='1')
    field_a2 = fields.Many2one('school.year',description='Fields A2',string='Année académique en cours (= année N)',related='year_id',readonly='1')
    field_a3 = fields.Selection([('long','Long'),('short', 'Short')],description='Fields A3',string='Type d''études', related='program_id.cycle_id.type',readonly='1')
    field_a4 = fields.Many2one('school.domain',description='Fields A4',string='Domaine d''études',related='program_id.speciality_id.domain_id',readonly='1')
    field_a5 = fields.Many2one('school.cycle',description='Fields A5',string='Cycle d''études et durée du cycle',related='program_id.cycle_id',readonly='1')
    field_a6 = fields.Many2one('school.section',description='Fields A6',string='Section d''études (Musique) ou AESS (tous les domaines)',related='program_id.speciality_id.section_id',readonly='1')
    field_a7 = fields.Many2one('school.track',description='Fields A7',string='Option',related='program_id.speciality_id.track_id',readonly='1')
    field_a8 = fields.Selection([('0','Free'),('1','Bac 1'),('2','Bac 2'),('3','Bac 3'),('4','Master 1'),('5','Master 2'),],description='Fields A8',string='Année d''études dans le cycle',related='source_bloc_id.level',readonly='1')
    field_a9 = fields.Selection([('1','Principale'),('2','Secondaire'),('3','Ternaire')], description='Fields A9',string='Inscriptions multiples', default='1')
    field_a10 = fields.Boolean(description='Fields A10',string='Jeunes Talents (Musique)', related='program_id.cycle_id.is_jeune_talent',readonly='1')
    field_a11 = fields.Selection([('A','Approfondie'),('D','Didactique'),('S','Specialisée')],description='Fields A11',string='Finalité du 2e cycle', related='program_id.cycle_id.type_second_cycle',readonly='1')
    field_a12 = fields.Many2one('school.speciality',description='Fields A12',string='Spécialité (Musique)',related='program_id.speciality_id',readonly='1')
    
    field_b1 = fields.Char(description='Fields B1',string='Nom de l''étudiant', related='student_id.lastname')
    field_b2 = fields.Char(description='Fields B2',string='Premier prénom de l''étudiant', related='student_id.firstname')
    field_b3 = fields.Char(description='Fields B3',string='Initiales des autres prénoms', related='student_id.initials')
    field_b4 = fields.Char(description='Fields B4',string='Numéro matricule', related='student_id.mat_number')
    field_b5 = fields.Selection([('male', 'Male'),('female', 'Female')],description='Fields B5',string='Sexe', related='student_id.gender')
    field_b6 = fields.Many2one('res.country',description='Fields B6',string='Nationalité', related='student_id.nationality_id')
    field_b7 = fields.Char(description='Fields B7',string='Lieu de naissance', related='student_id.birthplace')
    field_b8 = fields.Many2one('res.country',description='Fields B8',string='Pays du lieu de naissance', related='student_id.birthcountry')
    field_b9 = fields.Date(description='Fields B9',string='Date de naissance de l''étudiant', related='student_id.birthdate_date')
    field_b10 = fields.Char(description='Fields B10',string='Domicile légal en Belgique')
    field_b11 = fields.Char(description='Fields B11',string='Domicile légal à l''étranger')
    field_b12 = fields.Char(description='Fields B12',string='Numéro de Registre national', related='student_id.reg_number')
    
    field_c1 = fields.Selection([('r','Régulier'),('i','Irrégulier'),('l','Libre')], description='Fields C1',string='Régulier / Libre', default='r', required=True)
    field_c2 = fields.Date(description='Fields C2',string='Date d''abandon')
    field_c3 = fields.Selection([('A','Ancien'),('N','Nouveau')],description='Fields C3',string='Ancien/Nouveau', default='A', required=True)
    field_c4 = fields.Boolean(description='Fields C4',string='Etalement')
    field_c5 = fields.Selection([('0','Non'),('1','Mobilité européenne'),('2','Mobilité non-européenne')], description='Fields C5',string='Mobilité', related='student_id.mobility')
    field_c14 = fields.Selection([('1','Non'),('2','Oui, en FWB ou en Communauté germanophone'),('3','Oui, en Communauté flamande'),('4','Oui, à l’étranger')],description='Fields C14',string='Première génération', related='student_id.generation')
    field_c19 = fields.Selection([('AC','Mobilité académique'),('ST','Mobilité de stage'),('NA','Non applicable')],description='Fields C19',string='Type de mobilité', related='student_id.mob_type')
    
    field_d1 = fields.Selection([('1','Etudiant non finançable'),('2','Partiellement finançable'),('3','Étudiant finançable')],description='Fields D1',string='Nationalité de l''étudiant au regard du financement', default='3')
    #field_d2 = fields.Char(description='Fields D2',string='Modalité de l''inscription au regard du financement')
    field_d3 = fields.Selection([('B','Boursier'),('X','Non boursier'),('A','Bourse en attente'),('N','Bourse refusée')],description='Fields D3',string='Etudiant boursier')
    field_d4 = fields.Monetary(currency_field='company_currency_id', description='Fields D4',string='Minerval', related='invoice_id.amount_total',readonly='1')
    field_d5 = fields.Date(description='Fields D5',string='Date de réception du paiement du minerval', related='invoice_id.final_payment_date',readonly='1')
    field_d6 = fields.Monetary(currency_field='company_currency_id', description='Fields D6',string='Droit d''inscription spécifique (DIS)')
    field_d7 = fields.Date(description='Fields D7',string='Date de réception du paiement du droit d''inscription spécifique')
    field_d8 = fields.Selection([('0','Conditions normales'),('1','Conditions modestes')],description='Fields D8',string='Etudiant de condition modeste', related='student_id.modeste')
    
    field_e1 = fields.Selection([
        ('1','CESS délivré par un établissement de plein exercice'),
        ('2','CESS délivré par un établissementde promotion sociale'),
        ('3','CESS délivré par un Jury'),
        ('4','CESS délivré par un établissement de la Communauté flamande'),
        ('5','Diplôme ou certificat d''études étranger reconnu équivalent'),
        ('6','Diplôme délivré par un établissement d’enseignement supérieur'),
        ('7','Attestation de succès à l''un des examens d''admission'),
        ('8','Diplôme d''aptitude à accéder à l''enseignement supérieur (DAES)'),
        ('9','Diplômes autres pour lesquels l’équivalence n’est pas requise')],
        description='Fields E1',string='Titre d''accès à la première année du cycle court ou du premier cycle du type long')
    field_e2 = fields.Many2one('school.year', description='Fields E2',string='Année de délivrance du titre d''accès à la 1re année d''études')
    field_e3 = fields.Selection([
        ('GE1','Enseignement général'),
        ('TTI','Enseignement technique de transition'),
        ('TQ1','Enseignement technique de qualification'),
        ('AT1','Enseignement artistique de transition'),
        ('AQ1','Enseignement artistique de qualification'),
        ('PR1','Enseignement professionnel'),
        ('GE2','Autre enseignement général ou équivalent'),
        ('TE2','Autre enseignement technique ou équivalent'),
        ('AR2','Autre enseignement artistique ou équivalent'),
        ('PR2','Autre enseignement professionnel ou équivalent'),
        ('IN1','Inconnu')
        ], description='Fields E3',string='Type de secondaire obligatoire suivi')
    field_e4 = fields.Many2one('school.stat_etablissement', description='Fields E4',string='Etablissement d''enseignement de la FWB ou de la DG où le titre d''accès a été obtenu')
    field_e5 = fields.Many2one('res.country', description='Fields E5',string='Pays dans lequel le titre d''accès équivalent a été obtenu')
   
    field_f1 = fields.Selection([
        ('11','Dispense d’une ou plusieurs années d’études'),
        ('14','Equivalence d’études supérieures réussies à l’étranger'),
        ('15','Accès inconditionnel et sans enseignements complémentaires'),
        ('17','Accès en troisième année de bachelier du 1er cycle pour les premier prix'),
        ('20','Autres situations reconnues permettant l''accès à l''année d''études considérée'),
        ('21','Valorisation de crédits (Article 43)'),
        ('22','VAE (Article 44)'),
        ('23','Réduction de la durée minimale des études')
        ], description='Fields F1',string='Titre d''accès aux autres années que la première année des études de type court ou long')
    field_f2 = fields.Selection([
        ('10','Diplôme de l''enseignement supérieur de type court'),
        ('21','Diplôme de candidat ou de bachelier supérieur hors‐universités'),
        ('22','Diplôme de candidat ou de bachelier universitaire'),
        ('31','Diplôme final de l''enseignement supérieur hors‐universités'),
        ('32','Diplôme final de l''enseignement universitaire'),
        ('41','Diplôme de candidat ou de bachelier ou diplôme de l''enseignement supérieur de la Communauté flamande'),
        ('42','Diplôme final de l''enseignement supérieur de type long de la Communauté flamande'),
        ('50,','Diplôme de l''enseignement supérieur obtenu à l''étranger'),
        ('60','Diplôme délivré par le jury de la Fédération Wallonie‐Bruxelles'),
        ('70','Diplôme délivré par l’enseignement supérieur de promotion sociale'),
        ('80','Valorisation des acquis de l’expérience (VAE)'),
        ('90','Sans diplôme ni VAE')
        ], description='Fields F2',string='Diplôme obtenu dans l''enseignement supérieur')
    field_f3 = fields.Many2one('school.year', description='Fields F3',string='Année d''obtention du diplôme en F2')
    field_f4 = fields.Selection([
        ('10','Diplôme de l''enseignement supérieur de type court'),
        ('21','Diplôme de candidat ou de bachelier supérieur hors‐universités'),
        ('22','Diplôme de candidat ou de bachelier universitaire'),
        ('31','Diplôme final de l''enseignement supérieur hors‐universités'),
        ('32','Diplôme final de l''enseignement universitaire'),
        ('41','Diplôme de candidat ou de bachelier ou diplôme de l''enseignement supérieur de la Communauté flamande'),
        ('42','Diplôme final de l''enseignement supérieur de type long de la Communauté flamande'),
        ('50,','Diplôme de l''enseignement supérieur obtenu à l''étranger'),
        ('60','Diplôme délivré par le jury de la Fédération Wallonie‐Bruxelles'),
        ('70','Diplôme délivré par l’enseignement supérieur de promotion sociale'),
        ('80','Valorisation des acquis de l’expérience (VAE)'),
        ('90','Sans diplôme ni VAE')
        ], description='Fields F4',string='Autre diplôme obtenu dans l''enseignement supérieur (1)')
    field_f5 = fields.Many2one('school.year', description='Fields F5',string='Année d''obtention du diplôme en F4')
    field_f10 = fields.Many2one('res.country', description='Fields F10',string='Pays dans lequel le diplôme indiqué à la variable F2 a été obtenu')
    
    field_g2 = fields.Selection([
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], description='Fields G2',string='Activité principale au cours de l''année académique n‐1',compute='_compute_g_fields')
    field_g3 = fields.Many2one('school.stat_etablissement', description='Fields G3',string='Etablissement d''enseignement de la FWB concerné par G2',compute='_compute_g_fields')
    field_g4 = fields.Many2one('school.stat_domain', description='Fields G4',string='Domaine d''études concerné par G2',compute='_compute_g_fields')
    field_g5 = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], description='Fields G5',string='Année d''études se rapportant à G2',compute='_compute_g_fields')
    field_g6 = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ], description='Fields G6',string='Résultats se rapportant à G2',compute='_compute_g_fields')
    field_g7 = fields.Selection([
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], description='Fields G7',string='Activité principale au cours de l''année académique n‐2',compute='_compute_g_fields')
    field_g8 = fields.Many2one('school.stat_etablissement', description='Fields G8',string='Etablissement d''enseignement de la FWB concerné par G7',compute='_compute_g_fields')
    field_g9 = fields.Many2one('school.stat_domain', description='Fields G9',string='Domaine d''études concerné par G7',compute='_compute_g_fields')
    field_g10 = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], description='Fields G10',string='Année d''études se rapportant G7',compute='_compute_g_fields')
    field_g11 = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ], description='Fields G11',string='Résultats se rapportant à G7',compute='_compute_g_fields')
    field_g12 = fields.Selection([
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], description='Fields G12',string='Activité principale au cours de l''année académique n‐3',compute='_compute_g_fields')
    field_g13 = fields.Many2one('school.stat_etablissement', description='Fields G13',string='Etablissement d''enseignement de la FWB concerné par G12',compute='_compute_g_fields')
    field_g14 = fields.Many2one('school.stat_domain', description='Fields G14',string='Domaine d''études concerné par G12',compute='_compute_g_fields')
    field_g15 = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], description='Fields G15',string='Année d''études se rapportant à G12',compute='_compute_g_fields')
    field_g16 = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ], description='Fields G16',string='Résultats se rapportant à G12',compute='_compute_g_fields')
    field_g17 = fields.Selection([
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], description='Fields G17',string='Activité principale au cours de l''année académique n‐4',compute='_compute_g_fields')
    field_g18 = fields.Many2one('school.stat_etablissement', description='Fields G18',string='Etablissement d''enseignement de la FWB concerné par G17',compute='_compute_g_fields')
    field_g19 = fields.Many2one('school.stat_domain', description='Fields G19',string='Domaine d''études concerné par G17',compute='_compute_g_fields')
    field_g20 = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], description='Fields G20',string='Année d''études se rapportant à G17',compute='_compute_g_fields')
    field_g21 = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ], description='Fields G21',string='Résultats se rapportant à G17',compute='_compute_g_fields')
    field_g22 = fields.Selection([
        ('1','Enseignement secondaire non obligatoire (année préparatoire à l’enseignement supérieur, 4e cycle du secondaire, ...)'),
        ('2','Haute École de la Fédération Wallonie‐Bruxelles ou germanophone'),
        ('3','Université de la Fédération Wallonie‐Bruxelles'),
        ('4','Institut supérieur d''Architecture de la Fédération Wallonie‐Bruxelles'),
        ('5','École supérieure des Arts de la Fédération Wallonie‐Bruxelles'),
        ('6','Enseignement supérieur de promotion sociale de la Fédération Wallonie‐Bruxelles'),
        ('7','Enseignement supérieur de la Communauté flamande'),
        ('8','Enseignement supérieur à l''étranger'),
        ('9','Travail rémunéré'),
        ('10','Chômage'),
        ('11','Autre (année sabbatique, préparation à l''enseignement supérieur autre que dans le cadre de l''enseignement secondaire,...)'),
        ], description='Fields G22',string='Activité principale au cours de l''année académique n‐5',compute='_compute_g_fields')
    field_g23 = fields.Many2one('school.stat_etablissement', description='Fields G23',string='Etablissement d''enseignement de la FWB concerné par G22',compute='_compute_g_fields')
    field_g24 = fields.Many2one('school.stat_domain', description='Fields G24',string='Domaine d''études concerné par G22',compute='_compute_g_fields')
    field_g25 = fields.Selection([
            ('11','1re Bac'),
            ('12','2e Bac'),
            ('13','3e Bac'),
            ('14','4e Bac'),
            ('21','1re Master'),
            ('22','2e Master'),
            ('23','3e Master'),
            ('24','4e Master'),
            ('31','1re Spécialisation'),
            ('32','2e Spécialisation'),
            ('40','Doctorat'),
            ('99','Autres (CAPAES, AESS, Année préparatoire, etc.)'),
        ], description='Fields G25',string='Année d''études se rapportant à G22',compute='_compute_g_fields')
    field_g26 = fields.Selection([
            ('1','Réussite'),
            ('2','Refusé'),
        ], description='Fields G26',string='Résultats se rapportant à G22',compute='_compute_g_fields')
    
    field_g27 = fields.Many2one('res.country', description='Fields G27',string='Pays de l''activité académique se rapportant à G2')
    
    field_h1 = fields.Float(description='Fields H1',string='Résultats de la 1re session (juillet 2013)', related='first_session_result')
    field_h2 = fields.Float(description='Fields H2',string='Résultats de la 2e session (septembre 2013)', related='second_session_result')
    field_h3 = fields.Float(description='Fields H3',string='Résultats de session prolongée')
    field_h4 = fields.Date(description='Fields H4',string='Date du diplôme', related='program_id.graduation_date')
    
    @api.onchange('student_id.student_historic_entry_ids')
    @api.one
    def _compute_g_fields(self):
        year_minus_1 = self.year_id.previous if self.year_id else False
        year_minus_2 = year_minus_1.previous if year_minus_1 else False
        year_minus_3 = year_minus_2.previous if year_minus_2 else False
        year_minus_4 = year_minus_3.previous if year_minus_3 else False
        year_minus_5 = year_minus_4.previous if year_minus_4 else False
        if year_minus_1:
            _logger.info('Look for year %s' % year_minus_1.name)
            history = self.env['school.student_history_entry'].search([('student_id','=',self.student_id.id),('year_id','=',year_minus_1.id)])
            if history:
                _logger.info('Found année n-1')
                self.field_g2 = history.activite
                self.field_g3 = history.etablissement_id
                self.field_g4 = history.domain_id
                self.field_g5 = history.annee
                self.field_g6 = history.resultat
        if year_minus_2:
            _logger.info('Look for year %s' % year_minus_2)
            history = self.env['school.student_history_entry'].search([('student_id','=',self.student_id.id),('year_id','=',year_minus_2.id)])
            if history:
                _logger.info('Found année n-2')
                self.field_g7 = history.activite
                self.field_g8= history.etablissement_id
                self.field_g9= history.domain_id
                self.field_g10 = history.annee
                self.field_g11 = history.resultat
        if year_minus_3:
            history = self.env['school.student_history_entry'].search([('student_id','=',self.student_id.id),('year_id','=',year_minus_3.id)])
            if history:
                self.field_g12 = history.activite
                self.field_g13 = history.etablissement_id
                self.field_g14 = history.domain_id
                self.field_g15 = history.annee
                self.field_g16 = history.resultat
        if year_minus_4:
            history = self.env['school.student_history_entry'].search([('student_id','=',self.student_id.id),('year_id','=',year_minus_4.id)])
            if history:
                self.field_g17 = history.activite
                self.field_g18 = history.etablissement_id
                self.field_g19 = history.domain_id
                self.field_g20 = history.annee
                self.field_g21 = history.resultat
        if year_minus_5:
            history = self.env['school.student_history_entry'].search([('student_id','=',self.student_id.id),('year_id','=',year_minus_5.id)])
            if history:
                self.field_g22 = history.activite
                self.field_g23 = history.etablissement_id
                self.field_g24 = history.domain_id
                self.field_g25 = history.annee
                self.field_g26 = history.resultat
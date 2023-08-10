import logging

_logger = logging.getLogger(__name__)

from odoo import models, tools, api, fields

class ResCompanyCRLG(models.Model):
    _inherit = 'res.company'

    @api.model
    def init_crlg_social_medias(self):
        _logger.info("Init crlg social medias")
        company = self.env.company

        company.social_facebook = "https://www.facebook.com/ConservatoireLiege/"
        company.social_youtube = "https://www.youtube.com/channel/UCq7wqH7okutMExNgr_CMEVQ/videos"
        company.social_instagram = "https://www.instagram.com/conservatoireroyalliege/"
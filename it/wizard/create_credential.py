# Copyright (C) 2021 TREVI Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class NewCredential(models.TransientModel):
    _name = "it.wizard.credential"
    _description = "Create New Credential Wizard"

    @api.model
    def _get_aduser(self):
        import logging

        _l = logging.getLogger(__name__)
        _l.warning("_get_aduser: %s", self.env.context.get("active_id"))
        active_id = self.env.context.get("active_id")
        if active_id:
            ad = self.env["it.service.ad.object"].browse(active_id)
            return ad.id
        return False

    name = fields.Char(required=True)
    password = fields.Char(required=True)
    aduser_id = fields.Many2one("it.service.ad.object", "AD User", default=_get_aduser)
    equipment_id = fields.Many2one("it.equipment", "Asset")
    ad_id = fields.Many2one("it.service.ad", "Active Directory")
    site_id = fields.Many2one("it.site", "Site")
    partner_id = fields.Many2one("res.partner", "Partner")
    use_random = fields.Boolean("Random password")

    @api.onchange("aduser_id")
    def onchange_aduser(self):
        self.ad_id = False
        self.site_id = False
        self.partner_id = False
        self.equipment_id = False
        if self.aduser_id:
            if self.aduser_id.ad_id:
                self.ad_id = self.aduser_id.ad_id
            if self.aduser_id.ad_id.site_id:
                self.site_id = self.aduser_id.ad_id.site_id
            if self.aduser_id.ad_id.partner_id:
                self.partner_id = self.aduser_id.ad_id.partner_id
            if self.aduser_id.ad_id.equipment_id:
                self.equipment_id = self.aduser_id.ad_id.equipment_id

    @api.onchange("use_random")
    def onchange_use_random(self):
        ItAccess = self.env["it.access"]
        if self.use_random:
            self.password = ItAccess.get_random_string()

    @api.model
    def create(self, vals):

        # Get the password then remove it from the dictionary
        # so it doesn't get accidentaly written to the database.
        #
        plaintext = vals.get("password", False)
        vals["password"] = ""

        cred_vals = {
            "name": vals.get("name", False),
            "password": plaintext,
            "site_id": vals.get("site_id", False),
            "partner_id": vals.get("partner_id", False),
            "equipment_id": vals.get("equipment_id", False),
        }
        cred = self.env["it.access"].create(cred_vals)
        aduser = self.env["it.service.ad.object"].browse(vals.get("aduser_id", False))
        aduser.access_id = cred.id
        return super(NewCredential, self).create(vals)

from odoo import api, models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence")
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_type_id",
        string="Related Offers",
    )
    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Type name must be unique"),
    ]

    offer_count = fields.Integer(
        string='Offer Count',
        compute='_compute_offer_count',
    )

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    def action_view_offers(self):
        self.ensure_one()
        return {
            'name': 'Offers',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'estate.property.offer',
            'domain': [('property_type_id', '=', self.id)],
        }
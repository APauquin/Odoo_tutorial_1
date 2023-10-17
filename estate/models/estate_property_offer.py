from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    status = fields.Selection(
        [
            ("refused", "Refused"),
            ("sold", "Sold"),
        ],
        string="Status",
    )

    price = fields.Float(string="Offer Price")
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        string="Property Type",
        store=True,
    )

    _sql_constraints = [
        ("price_check", "CHECK(price > 0)", "Offer Price must be strictly positive"),
    ]

    validity = fields.Integer(string="Validity (days)", default=7)
    deadline = fields.Date(
        string="Deadline",
        compute="_compute_deadline",
        inverse="_set_deadline",
        store=True,
    )

    @api.depends("create_date", "validity")
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.deadline = fields.Datetime.now() + timedelta(
                    days=record.validity
                )

    def _set_deadline(self):
        for record in self:
            if record.deadline and record.create_date:
                record.validity = (record.deadline - record.create_date.date()).days

    def action_accept(self):
        for record in self:
            if record.status == "refused":
                raise UserError(_("Refused offers cannot be sold."))
            record.property_id.write(
                {
                    "buyer_id": record.partner_id.id,
                    "selling_price": record.price,
                }
            )
            record.status = "sold"
        return True

    def action_refuse(self):
        for record in self:
            if record.status == "sold":
                raise UserError("Sold offers cannot be refused.")
            record.status = "refused"
        return True
    
    @api.model
    def create(self, vals):
        property_id = self.env['estate.property'].browse(vals.get('property_id'))
        if property_id:
            existing_offers = self.search([('property_id', '=', property_id.id)])
            for offer in existing_offers:
                if offer.price >= vals.get('price', 0):
                    raise UserError("Your offer is lower than an existing offer!")
        new_offer = super(EstatePropertyOffer, self).create(vals)
        property_id.write({'state': 'offer_received'})

        return new_offer

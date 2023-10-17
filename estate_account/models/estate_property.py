from odoo import models, _, Command

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        result = super(EstateProperty, self).action_sold()

        price_of_sale = {
            'name': 'Sale price',
            'quantity': 1,
            'price_unit': self.selling_price,
        }

        line_6_percent = {
            'name': '6% of the selling price',
            'quantity': 1,
            'price_unit': self.selling_price * 0.06,
        }

        line_admin_fee = {
            'name': 'Administrative fees',
            'quantity': 1,
            'price_unit': 100.00,
        }

        invoice_vals = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                Command.create(price_of_sale),
                Command.create(line_6_percent),
                Command.create(line_admin_fee),
            ]
        }

        invoice = self.env['account.move'].create(invoice_vals)

        return {"type": "ir.actions.act_window_close"}
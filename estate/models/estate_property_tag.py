from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    color = fields.Char(string="Color", default='#d10000')
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag name must be unique'),
    ]

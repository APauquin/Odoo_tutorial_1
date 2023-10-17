from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    sequence = fields.Integer(string='Sequence')
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        string="Available",
        copy=False,
        default=lambda self: fields.Date.add(fields.Date.context_today(self), days=90),
    )
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="No. of Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area")
    garden_area = fields.Integer(string="Garden Area")
    total_area = fields.Float(
        string="Total Area", compute="_compute_total_area", store=True
    )
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Has Garage?")
    garden = fields.Boolean(string="Has Garden?")
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        string="Garden Orientation",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
        ],
        string="State",
        required=True,
        copy=False,
        default="new",
    )
    status = fields.Selection(
        [
            ("refused", "Refused"),
            ("sold", "Sold"),
        ],
        string="Status",
    )
    active = fields.Boolean(string="Active", default=True)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
    )
    tag_ids = fields.Many2many(
        "estate.property.tag",
    )
    best_price = fields.Float(
        string="Best Offer", compute="_compute_best_price", store=True
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    _sql_constraints = [
        (
            "expected_price_check",
            "CHECK(expected_price > 0)",
            "Expected Price must be strictly positive",
        ),
        (
            "selling_price_check",
            "CHECK(selling_price >= 0)",
            "Selling Price must be positive",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains("expected_price", "selling_price")
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue

            min_selling_price = 0.9 * record.expected_price
            if (
                float_compare(
                    record.selling_price, min_selling_price, precision_digits=2
                )
                < 0
            ):
                raise UserError(
                    "The selling price cannot be lower than 90% of the expected price."
                )

    def action_cancel(self):
        if self.state == "sold":
            raise UserError(("You cannot cancel a sold property."))
        self.state = "new"

    def action_sold(self):
        if self.state == "cancelled":
            raise UserError(("You cannot sell a canceled property."))
        self.state = "sold"

    @api.ondelete(at_uninstall=False)
    def _check_state_before_deletion(self):
        for record in self:
            if record.state != 'new':
                raise UserError("You cannot delete a property which is not 'New' or 'Canceled'.")

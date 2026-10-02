from odoo import api, fields, models


class VendingMachine(models.Model):
    _name = "vending.machine"
    _description = "Vending Machine"
    _order = "name"

    name = fields.Char(required=True, default="New Machine")
    code = fields.Char(required=True, copy=False, index=True)
    partner_id = fields.Many2one("res.partner", string="Customer / Location")
    stock_location_id = fields.Many2one(
        "stock.location",
        string="Stock Location",
        domain="[('usage', '=', 'internal')]",
        help="Optional Odoo inventory location representing the stock physically inside this machine.",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("offline", "Offline"), ("online", "Online"), ("maintenance", "Maintenance")],
        default="offline",
        required=True,
    )
    last_seen = fields.Datetime(readonly=True)
    slot_ids = fields.One2many("vending.slot", "machine_id", string="Slots")
    slot_count = fields.Integer(compute="_compute_slot_count")
    notes = fields.Text()

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "The machine code must be unique.",
    )

    @api.depends("slot_ids")
    def _compute_slot_count(self):
        for machine in self:
            machine.slot_count = len(machine.slot_ids)

    def action_mark_online(self):
        self.write({"state": "online", "last_seen": fields.Datetime.now()})

    def action_mark_offline(self):
        self.write({"state": "offline"})


class VendingSlot(models.Model):
    _name = "vending.slot"
    _description = "Vending Machine Slot"
    _order = "machine_id, sequence, code"

    sequence = fields.Integer(default=10)
    machine_id = fields.Many2one("vending.machine", required=True, ondelete="cascade", index=True)
    code = fields.Char(required=True, help="Physical selection code, e.g. A1, A2, A3.")
    product_id = fields.Many2one("product.product", string="Product")
    price = fields.Float(digits="Product Price", help="Selling price used by the vending application.")
    capacity = fields.Integer(default=7)
    quantity = fields.Integer(string="Current Qty", default=0)
    gpio_pin = fields.Integer(string="GPIO Pin", help="Prototype Raspberry Pi GPIO assignment.")
    active = fields.Boolean(default=True)

    _machine_code_unique = models.Constraint(
        "UNIQUE(machine_id, code)",
        "The slot code must be unique per machine.",
    )


class VendingSlotDispense(models.Model):
    _inherit = "vending.slot"

    def action_test_dispense(self):
        self.ensure_one()
        command = self.env["vending.command"].create({
            "machine_id": self.machine_id.id,
            "slot_id": self.id,
            "command": "dispense",
        })
        return {
            "type": "ir.actions.act_window",
            "name": "Vending Command",
            "res_model": "vending.command",
            "res_id": command.id,
            "view_mode": "form",
            "target": "current",
        }

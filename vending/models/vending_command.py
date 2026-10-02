from odoo import fields, models


class VendingCommand(models.Model):
    _name = "vending.command"
    _description = "Vending Command"
    _order = "create_date desc"

    machine_id = fields.Many2one("vending.machine", required=True, ondelete="cascade", index=True)
    slot_id = fields.Many2one("vending.slot", required=True, ondelete="cascade", index=True)
    command = fields.Selection([("dispense", "Dispense")], default="dispense", required=True)
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
        default="pending",
        required=True,
        index=True,
    )
    requested_at = fields.Datetime(default=fields.Datetime.now, required=True)
    completed_at = fields.Datetime(readonly=True)
    error_message = fields.Text(readonly=True)

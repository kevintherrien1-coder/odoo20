from odoo import fields, models


class VendingTransaction(models.Model):
    _name = "vending.transaction"
    _description = "Vending Transaction"
    _order = "create_date desc"

    machine_id = fields.Many2one(
        "vending.machine",
        required=True,
        ondelete="restrict",
    )

    slot_id = fields.Many2one(
        "vending.slot",
        required=True,
        ondelete="restrict",
    )

    product_id = fields.Many2one(
        "product.product",
        related="slot_id.product_id",
        store=True,
    )

    amount = fields.Monetary(
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    payment_transaction_id = fields.Many2one(
        "payment.transaction",
        string="Payment Transaction",
        readonly=True,
    )

    command_id = fields.Many2one(
        "vending.command",
        readonly=True,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("pending", "Payment Pending"),
        ("paid", "Paid"),
        ("dispensed", "Dispensed"),
        ("failed", "Failed"),
    ], default="draft", required=True)
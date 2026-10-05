from odoo import http, fields
from odoo.http import request


class VendingAPI(http.Controller):

    def _authenticate_machine(self, machine_code, api_token):
        if not machine_code or not api_token:
            return None

        return request.env["vending.machine"].sudo().search([
            ("code", "=", machine_code),
            ("api_token", "=", api_token),
        ], limit=1)

    @http.route(
        "/vending/api/command/next",
        type="jsonrpc",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def next_command(self, machine_code=None, api_token=None):

        machine = self._authenticate_machine(
            machine_code,
            api_token,
        )

        if not machine:
            return {
                "success": False,
                "error": "invalid_machine_or_token",
            }

        # Machine is alive
        machine.sudo().write({
            "last_seen": fields.Datetime.now(),
            "state": "online",
        })

        command = request.env["vending.command"].sudo().search([
            ("machine_id", "=", machine.id),
            ("state", "=", "pending"),
            ("slot_id.quantity", ">", 0),
        ], order="create_date asc", limit=1)

        if not command:
            return {
                "success": True,
                "command": None,
            }

        # Reserve the command so it won't be returned again
        command.write({
            "state": "processing",
        })

        return {
            "success": True,
            "command": {
                "id": command.id,
                "action": command.command,
                "slot": command.slot_id.code,
                "gpio_pin": command.slot_id.gpio_pin,
                "product": command.slot_id.product_id.display_name,
            }
        }

    @http.route(
        "/vending/api/command/done",
        type="jsonrpc",
        auth="none",
        methods=["POST"],
        csrf=False,
    )

    def command_done(
        self,
        machine_code=None,
        api_token=None,
        command_id=None,
    ):

        machine = self._authenticate_machine(
            machine_code,
            api_token,
        )

        if not machine:
            return {
                "success": False,
                "error": "invalid_machine_or_token",
            }

        command = request.env["vending.command"].sudo().search([
            ("id", "=", command_id),
            ("machine_id", "=", machine.id),
            ("state", "=", "processing"),
        ], limit=1)

        if not command:
            return {
                "success": False,
                "error": "command_not_found",
            }

        slot = command.slot_id

        if slot.quantity <= 0:
            return {
                "success": False,
                "error": "slot_out_of_stock",
            }

        # Decrease slot inventory only after successful dispense
        slot.sudo().write({
            "quantity": slot.quantity - 1,
        })

        # Mark command as completed
        command.write({
            "state": "done",
            "completed_at": fields.Datetime.now(),
        })

        return {
            "success": True,
            "remaining_quantity": slot.quantity,
        }

    @http.route(
        "/vending/api/command/failed",
        type="jsonrpc",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def command_failed(
        self,
        machine_code=None,
        api_token=None,
        command_id=None,
        error_message=None,
    ):

        machine = self._authenticate_machine(
            machine_code,
            api_token,
        )

        if not machine:
            return {
                "success": False,
                "error": "invalid_machine_or_token",
            }

        command = request.env["vending.command"].sudo().search([
            ("id", "=", command_id),
            ("machine_id", "=", machine.id),
            ("state", "=", "processing"),
        ], limit=1)

        if not command:
            return {
                "success": False,
                "error": "command_not_found",
            }

        command.write({
            "state": "failed",
            "completed_at": fields.Datetime.now(),
            "error_message": error_message,
        })

        return {
            "success": True,
        }

class VendingWebsite(http.Controller):

    @http.route(
        "/vending/<string:machine_code>",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def vending_machine_page(self, machine_code, **kwargs):

        machine = request.env["vending.machine"].sudo().search([
            ("code", "=", machine_code),
        ], limit=1)

        if not machine:
            return request.not_found()

        slots = request.env["vending.slot"].sudo().search([
            ("machine_id", "=", machine.id),
        ], order="code asc")

        return request.render(
            "vending.vending_machine_page",
            {
                "machine": machine,
                "slots": slots,
            }
        )
{
    "name": "Vending",
    "summary": "Manage vending machines and their product slots",
    "version": "20.0.1.0.1",
    "category": "Inventory",
    "license": "LGPL-3",
    "depends": ["base", "product", "stock", "sale_management", "website", "payment"],
    "data": [
        "security/ir.access.csv",
        "views/vending_machine_views.xml",
        "views/vending_command_views.xml",
        "views/vending_menus.xml",
        'views/vending_website_templates.xml',
    ],
    "application": True,
    "installable": True,
}

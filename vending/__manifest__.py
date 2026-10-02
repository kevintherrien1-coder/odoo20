{
    "name": "Vending",
    "summary": "Manage vending machines and their product slots",
    "version": "20.0.1.0.0",
    "category": "Inventory",
    "license": "LGPL-3",
    "depends": ["base", "product", "stock", "sale_management"],
    "data": [
        'security/ir.access.csv',
        "views/vending_machine_views.xml",
        "views/vending_menus.xml",
    ],
    "application": True,
    "installable": True,
}

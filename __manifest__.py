{
    'name': 'Returns Management',
    'version': '1.0',
    'summary': 'Manage Purchase and Sales Returns',
    'description': """
        This module handles both purchase and sales returns 
        with full integration with inventory and accounting.
    """,
    'author': 'Mohamed Osman',
    'website': 'https://www.yourwebsite.com',
    'category': 'Inventory',
    'depends': ['base', 'stock', 'account', 'purchase', 'sale','sale_management'],
    'data': [
        'data/sequences.xml',
        'security/ir.model.access.csv',
        'security/return_security.xml',
        'views/return_order_views.xml',
        'views/return_order_line_views.xml',
        # 'reports/return_report.xml',
        'views/menu.xml',

    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'returns_management/static/src/xml/dashboard_template.xml',
    #         'returns_management/static/src/js/return_dashboard.js',
    #     ],
    # },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

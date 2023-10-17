{
    'name': 'Estate',
    'version': '1.0',
    'category': 'Real Estate',
    'summary': 'My Real Estate Module',
    'sequence': 15,
    'depends': ['base'],
    'data': [
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/estate_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
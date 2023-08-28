{
    'name': 'Web List View Fixed Table Header',
    'version': '16.0.1.0.1',
    'category': 'Widget',
    'sequence': 15,
    'summary': 'Web List View Fixed Table Header',
    'author': 'Andre Leander',
    'website': 'https://github.com/ito-invest-lu/horizon',
    'depends': ['web','base'],
    'data': [
        'views/web_list_view_sticky.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

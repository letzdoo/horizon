{
    'name': 'Web List View Fixed Table Header',
    'version': '16.0.0.1',
    'category': 'Widget',
    'sequence': 15,
    'summary': 'Web List View Fixed Table Header',
    'description': """
Web List View Fixed Table Header
=================================
* Fixed (sticky) list view table header, very helpful when dealing with many record.
""",
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

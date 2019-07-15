def get_db_dict():
    from django_sorcery.db import databases
    return {
        'default': databases.get('default').bind
    }

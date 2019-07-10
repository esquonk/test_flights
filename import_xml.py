import django

from data_import.xml_importer import XmlImporter
from db.engine import Session


def run():
    django.setup()
    session = Session()

    with open("RS_Via-3.xml", 'rt') as f:
        importer = XmlImporter(session, f, "3")
        importer.run()

    session.commit()


if __name__ == "__main__":
    run()

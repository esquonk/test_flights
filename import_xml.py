import django

from fares.data_import.xml_importer import XmlImporter


def run():
    django.setup()

    with open("RS_Via-3.xml", 'rt') as f:
        importer = XmlImporter(f, "3")
        importer.run()
    with open("RS_ViaOW.xml", 'rt') as f:
        importer = XmlImporter(f, "OW")
        importer.run()


if __name__ == "__main__":
    run()

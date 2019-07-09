from data_import.xml_importer import XmlImporter


def run():
    importer = XmlImporter()

    with open("RS_Via-3.xml", 'rt') as f:
        importer.run(f)


if __name__ == "__main__":
    run()

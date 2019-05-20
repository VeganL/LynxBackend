from configparser import ConfigParser

def readEmailConfig(filename='config.ini',section='gmail'):
    parser = ConfigParser()
    parser.read(filename)

    email = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            email[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return email

import os 

import csv 

filename = "names.csv"

def create_vcard(file):
    last_name, first_name, title, email, phone = file
    content = f"""BEGIN:VCARD
    VERSION:2.1
    N:{last_name};{first_name}
    FN:{first_name} {last_name}
    ORG:Authors, Inc.
    TITLE:{title}
    TEL;WORK;VOICE:{phone}
    ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
    EMAIL;PREF;INTERNET:{email}
    REV:20150922T195243Z
    END:VCARD
    """
    return content

def read_csv(file_name):
    data = []
    with open(file_name,"r") as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            data.append(row)
    return data
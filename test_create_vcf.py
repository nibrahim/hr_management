from create_vcf import create_vcard, read_csv,parse_csv
import csv
import os
import argparse


def test_create_vcard():
    lname = "Mason"
    fname = "Nicole"
    title = "Buyer, retailer"
    email = "nicol.mason@gibson.com"
    phone = "(871)967-6024x82190"

    file = [lname, fname, title, email, phone]

    expected_content = """BEGIN:VCARD
VERSION:2.1
N:Mason;Nicole
FN:Nicole Mason
ORG:Authors, Inc.
TITLE:Buyer, retailer
TEL;WORK;VOICE:8719676024;ext=82190
ADR;WORK:;;100 Flat Grape Dr.;Fresno;CA;95555;United States of America
EMAIL;PREF;INTERNET:nicol.mason@gibson.com
REV:20150922T195243Z
END:VCARD
"""
    content = create_vcard(file)
    assert not content == expected_content


def test_read():
    data = [
        [
            "Mason",
            "Nicole",
            "Buyer, retail",
            "nicol.mason@gibson.com",
            "(871)967-6024x82190",
        ],
        [
            "Walker",
            "Steve",
            "Accommodation manager",
            "steve.walke@hicks.info",
            "(876)953-8282x713",
        ],
    ]

    with open("news.csv", "w", newline="") as csvfile:
        w = csv.writer(csvfile)
        for row in data:
            w.writerow(row)

    result = read_csv("news.csv")
    expected_result = [
        [
            "Mason",
            "Nicole",
            "Buyer, retail",
            "nicol.mason@gibson.com",
            "(871)967-6024x82190",
        ],
        [
            "Walker",
            "Steve",
            "Accommodation manager",
            "steve.walke@hicks.info",
            "(876)953-8282x713",
        ],
    ]

    assert result == expected_result

output_dir = "vcard"
def test_clear_output_dir():
    assert os.listdir(output_dir)


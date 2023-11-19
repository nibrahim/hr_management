import os
import requests
import csv
import logging
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog="create_vcf.py", description="Generates sample employee database as csv"
    )
    parser.add_argument("input_file", help="Name of input csv file")
    parser.add_argument("output_dir", help="Output directory for vCards and QR codes")
    parser.add_argument(
        "-n",
        "--number",
        help="Number of records to generate",
        action="store",
        type=int,
        default=10,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print detailed logging",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-q", "--add_qr", help="Add QR codes", action="store_true", default=False
    )
    parser.add_argument(
        "-s", "--qr_size", help="Size of QR code", type=int, default=500
    )
    parser.add_argument(
        "-a", "--address", help="Employee address", type=str, default = "100 Flat Grape Dr.;Fresno;CA;95555;United States of America"
    )
    args = parser.parse_args()
    return args


def setup_logging(log_level):
    global logger
    logger = logging.getLogger("vcf_log")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("run.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s | %(filename)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def create_vcard(file, address):
    last_name, first_name, title, email, phone = file
    content = f"""BEGIN:VCARD
    VERSION:2.1
    N:{last_name};{first_name}
    FN:{first_name} {last_name}
    ORG:Authors, Inc.
    TITLE:{title}
    TEL;WORK;VOICE:{phone}
    ADR;WORK:;;{address}
    EMAIL;PREF;INTERNET:{email}
    REV:20150922T195243Z
    END:VCARD
    """
    return content



def read_csv(file_name):
    data = []
    if os.path.isfile(file_name):
        with open(file_name, "r") as file:
            csv_file = csv.reader(file)
            data = [row for row in csv_file]
    else:
        logger.error(f"File not found: {file_name}")
    return data


def insert_employee_data(row_data, conn):
    cursor = conn.cursor()

    insert_query = '''
        INSERT INTO Employees (LastName, FirstName, Title, Email, Phone, Address)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, row_data)
    conn.commit()

    cursor.close()





def parse_csv(file_name, args):
    data = read_csv(file_name)
    counter = 0

    for row in data[: args.number]:
        vcard_content = create_vcard(row, args.address)
        create_vcard_file(row, vcard_content, args)
        if args.add_qr:
            generate_qr_code(row, vcard_content, args)
        counter += 1

        if args.number and counter >= args.number:
            break

    logger.info(f"Processed {counter} records")


counter = 0

def create_vcard_file(row_data, content, args):
    global counter

    file_path = os.path.join(
        args.output_dir, f"{row_data[1].lower()}_{row_data[0].lower()}.vcf"
    )

    if os.path.exists(file_path):
        logger.warning(f"File already exists: {file_path}")
    else:
        with open(file_path, "w") as file:
            file.write(content)
            counter += 1
            logger.info(f"Created vCard ({counter}): {file_path}")


def generate_qr_code(row_data, content, args):
    qr_url = requests.get(
        f"https://chart.googleapis.com/chart?cht=qr&chs={args.qr_size}x{args.qr_size}&chl={content}"
    )
    file_path = f"{args.output_dir}/{row_data[1].lower()}_{row_data[0].lower()}.qr.png"

    if os.path.exists(file_path):
        logger.warning(f"File already exists: {file_path}")
    else:
        if os.access(args.output_dir, os.W_OK):
            with open(file_path, "wb") as file:
                file.write(qr_url.content)
                logger.info(f"Created QR code: {file_path}")
        else:
            logger.warning(f"No write access to directory: {args.output_dir}")
            print(f"No write access to directory: {args.output_dir}")


def clear_output_dir(output_dir):
    if os.path.exists(output_dir):
        files_in_dir = os.listdir(output_dir)

        for file in files_in_dir:
            file_path = os.path.join(output_dir, file)

            if os.path.isfile(file_path):
                os.remove(file_path)

def main():
    args = parse_args()
    if args.verbose:
        setup_logging(logging.DEBUG)
    else:
        setup_logging(logging.INFO)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    else:
        clear_output_dir(args.output_dir)
    parse_csv(args.input_file, args)


if __name__ == "__main__":
    main()

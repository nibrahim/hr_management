import os
import requests
import csv
import logging
import argparse
import psycopg2
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        prog="create_vcf.py", description="Generate employee database"
    )
    parser.add_argument("--input_type", help="Specify the data source",choices=['file', 'db'], required=True)
    parser.add_argument("--input_file", help="Name of input csv file")
    parser.add_argument("--output_dir", help="Output directory for vCards and QR codes")
    parser.add_argument("--db_name", help="Name of the database")
    parser.add_argument("--db_user", help="Database username")

    parser.add_argument("--table_name", help="Name of the database table", required=True)

    parser.add_argument("-n","--number",help="Number of records to generate",action="store",type=int,default=10,)
    parser.add_argument("-v","--verbose",help="Print detailed logging",action="store_true",default=False,)
    parser.add_argument("-q", "--add_qr", help="Add QR codes", action="store_true", default=False)
    parser.add_argument("-s", "--qr_size", help="Size of QR code", type=int, default=500)
    parser.add_argument( "-a", "--address", help="Employee address", type=str, default="100 Flat Grape Dr.;Fresno;CA;95555;United States of America")
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

    if log_level == logging.DEBUG:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.WARNING)

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

def create_emp_db_and_table(db_name, db_user):
    try:
        conn = psycopg2.connect(dbname='emp_db', user=db_user)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.close()
        conn.close()

        conn = psycopg2.connect(dbname=db_name, user=db_user)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                employee_id SERIAL PRIMARY KEY,
                last_name VARCHAR(255) NOT NULL,
                first_name VARCHAR(255) NOT NULL,
                title VARCHAR(255),
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating database and table: {e}")
        return False
    
def insert_csv_to_db(csv_file, db_name, db_user):
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user)

    cursor = conn.cursor()

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader) 
        for row in reader:
            cursor.execute(
                "INSERT INTO Employees (last_name, first_name, title, email, phone) VALUES (%s, %s, %s, %s, %s)",
                row[:5])

    conn.commit()
    cursor.close()
    conn.close()

def truncate_csv(csv_file):
    with open(csv_file, 'w') as file:
        file.truncate()

def fetch_data_from_db():
    conn = psycopg2.connect(
        dbname="emp_db",
        user="anusha")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Employees")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def create_leaves_table(args):
    try:
        conn = psycopg2.connect(dbname='emp_db', user='anusha')
        cursor = conn.cursor()

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {args.table_name} (
                employee_id INTEGER NOT NULL,
                leave_date DATE NOT NULL,
                reason VARCHAR(255) NOT NULL,
                PRIMARY KEY (employee_id, leave_date)
            )
        ''')
        conn.commit()
        cursor.close()
        print(f"Table '{args.table_name}' created successfully!")
    except psycopg2.Error as e:
        print("Error creating table:", e)

def add_fk_constraint():
    conn = psycopg2.connect(dbname='emp_db', user='anusha')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            ALTER TABLE IF EXISTS attendance
            DROP CONSTRAINT IF EXISTS fk_employee_id
        ''')
        conn.commit()

        cursor.execute('''
            ALTER TABLE attendance
            ADD CONSTRAINT fk_employee_id
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ''')
        conn.commit()
        cursor.close()
        #print("Foreign key constraint added successfully!")
    except psycopg2.IntegrityError as e:
        print("Error adding foreign key constraint:", e)

def get_leaves_by_employee_id(employee_id):
    conn = psycopg2.connect(dbname='emp_db', user='anusha')
    cursor = conn.cursor()

    cursor.execute('SELECT leave_date, reason FROM Attendance WHERE employee_id = %s', (employee_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_leave_count_for_employee(employee_id):
    conn = psycopg2.connect(dbname='emp_db', user='anusha')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT COUNT(*) FROM Attendance WHERE employee_id = %s',
        (employee_id,)
    )
    leave_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return leave_count

def insert_attendance_records():
    try:
        conn = psycopg2.connect(dbname='emp_db', user='anusha')
        cursor = conn.cursor()

        records = [
            (datetime(2023, 11, 25), 'Vacation'),
            (datetime(2023, 11, 26), 'Sick leave'),
            (datetime(2023, 11, 27), 'Personal leave'),
            (datetime(2023, 11, 28), 'Casual leave'),
            (datetime(2023, 11, 29), 'Vacation'),
            (datetime(2023, 11, 30), 'Sick leave'),
            (datetime(2023, 12, 1), 'Personal leave'),
            (datetime(2023, 12, 2), 'Casual leave'),
            (datetime(2023, 12, 3), 'Vacation'),
            (datetime(2023, 12, 4), 'Sick leave')
        ]

        sql = "INSERT INTO attendance (employee_id, leave_date, reason) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING"

        employee_ids = list(range(1, 100))  
        index = 0
        for employee_id in employee_ids:  
            cursor.execute(sql, (employee_id, records[index][0], records[index][1]))
            index = (index + 1) % len(records)

        conn.commit()
        cursor.close()
        conn.close()

        print("Records inserted successfully!")
    except psycopg2.Error as e:
        print("Error inserting records:", e)

insert_attendance_records()


def access_data_generate_vcards(employee_data, args):
    #print("Fetched details:", employee_data)
    counter = 0

    for row in employee_data[:args.number]:
        vcard_content = create_vcard(row[:5], args.address)  
        create_vcard_file(row[:5], vcard_content, args)
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
        args.output_dir, f"{str(row_data[1]).lower()}_{str(row_data[0]).lower()}.vcf"
    )
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(content)
            counter += 1
            logger.info(f"Created vCard ({counter}): {file_path}")


def generate_qr_code(row_data, content, args):
    qr_url = requests.get(
        f"https://chart.googleapis.com/chart?cht=qr&chs={args.qr_size}x{args.qr_size}&chl={content}")
    file_path = os.path.join(
        args.output_dir, f"{str(row_data[1]).lower()}_{str(row_data[0]).lower()}.qr.png")

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

    create_leaves_table(args)
    add_fk_constraint()

    data_from_db = fetch_data_from_db()  
    if data_from_db: 
        access_data_generate_vcards(data_from_db, args)
        logger.info("Details successfully loaded to output directory")
    else:
        logger.error("Failed to fetch data from the database.")

    while True:
        try:
            employee_id_to_check = int(input("Enter the employee ID to get leave records: "))
            if employee_id_to_check == 0:
                break

            leave_date = input("Enter the date (YYYY-MM-DD) to get leave records: ")

            conn = psycopg2.connect(dbname='emp_db', user='anusha')
            cursor = conn.cursor()

            cursor.execute(
    'SELECT e.employee_id, e.first_name, e.last_name, a.leave_date, a.reason '
    'FROM employees e '
    'JOIN attendance a ON e.employee_id = a.employee_id '
    'WHERE e.employee_id = %s AND a.leave_date = %s',
    (employee_id_to_check, leave_date))

            records = cursor.fetchall()

            if not records:
                print("No records found for the provided details.")
            else:
                print("Records Found:")
                for record in records:
                    print(f"Employee ID: {record[0]}, Name: {record[2]} {record[1]}, Date: {record[3]}, Reason: {record[4]}")

                    leave_count = get_leave_count_for_employee(employee_id_to_check)
                    print(f"Total leave count for Employee {employee_id_to_check}: {leave_count}")

            cursor.close()
            conn.close()
        except ValueError:
            print("Please enter a valid number for employee ID.")

if __name__ == "__main__":
    main()



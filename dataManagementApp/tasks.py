from celery import shared_task
import csv
import io
from django.db import connection, transaction

BATCH_SIZE = 1000  

@shared_task
def process_csv_file(file_data, table_name):
    try:
        csv_reader = csv.DictReader(io.StringIO(file_data))
        batch = []
        columns = None

        for row in csv_reader:
            if not columns:
                columns = ', '.join(row.keys())

            values = tuple(row.values())
            batch.append(values)

            if len(batch) >= BATCH_SIZE:
                insert_bulk(table_name, columns, batch)
                batch = []  

        if batch:
            insert_bulk(table_name, columns, batch)

        return {'message': 'CSV imported successfully'}

    except Exception as e:
        return {'error': str(e)}

def insert_bulk(table_name, columns, batch):
    print("Processing bulk insert...")

    if not table_name.isidentifier():
        raise ValueError("Invalid table name")

    placeholders = ', '.join(['%s'] * len(batch[0]))  
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    try:
        with connection.cursor() as cursor:
            with transaction.atomic():
                cursor.executemany(query, batch)
    except Exception as e:
        print(f"Error inserting batch: {str(e)}")

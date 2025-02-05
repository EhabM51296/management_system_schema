from celery import shared_task
import csv
import io
from django.db import connection

@shared_task
def process_csv_file(file_data, table_name):
    try:
        csv_reader = csv.DictReader(io.StringIO(file_data))
        for row in csv_reader:
            with connection.cursor() as cursor:
                columns = ', '.join(row.keys())
                values = ', '.join([f"'{value}'" for value in row.values()])
                cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values});")
                
        return {'message': 'CSV imported successfully'}

    except Exception as e:
        return {'error': str(e)}

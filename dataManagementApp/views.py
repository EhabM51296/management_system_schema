from django.http import JsonResponse
from django.db import connection, transaction
import json
from dataManagementApp.models import SchemaData
from dataManagementApp.tasks import process_csv_file
from .utils import construct_Add_column_query, construct_alter_column_query, construct_create_table_query, construct_drop_column_query, create_field_definitions, save_schema_data
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# create a new table
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_table(request):
        data = json.loads(request.body)
        table_name = data.get('table_name')
        fields = data.get('fields')

        if not table_name.isidentifier() or not fields:
            return JsonResponse({"error": "Missing table_name or fields"})

        if not isinstance(fields, dict):
            return JsonResponse({"error": "Fields should be a dictionary"})
        
        try:
            # Start a transaction block
            with transaction.atomic():
                # Validate the field definitions and create field SQL
                field_definitions = create_field_definitions(fields)
                create_table_query = construct_create_table_query(table_name, field_definitions)
                
                with connection.cursor() as cursor:
                    cursor.execute(create_table_query)

                # Save schema data to the database
                save_schema_data(table_name, fields)

                return JsonResponse({
                    "message": "Schema created successfully",
                    "create_table_query": create_table_query
                })

        except Exception as e:
            return JsonResponse({
                "error": f"An error occurred while creating the schema: {str(e)}"
            })

# update schema of a table
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_table(request):
        data = json.loads(request.body)
        table_name = data.get('table_name')
        new_field = data.get('new_field')  
        update_field = data.get('update_field')  
        delete_field = data.get('delete_field') 

        if not table_name:
            return JsonResponse({'error': 'table_name is required'})

        if not SchemaData.objects.filter(table_name=table_name).exists():
            return JsonResponse({'error': f'Table {table_name} does not exist'})
        
        with connection.cursor() as cursor:
            try:
                with transaction.atomic():
                    schema_metadata = SchemaData.objects.get(table_name=table_name)
                    old_fields = schema_metadata.fields
                    if isinstance(old_fields, str):
                        old_fields = json.loads(old_fields)
                        
                    if new_field:
                        field_definitions = create_field_definitions(new_field)
                        alter_fields_query = construct_Add_column_query(table_name, field_definitions)
                        cursor.execute(alter_fields_query)

                        for field_name, add_field in new_field.items():
                            old_fields[field_name] = add_field
                            
                    if update_field:
                        alter_fields_query = construct_alter_column_query(table_name, update_field)
                        cursor.execute(alter_fields_query)
                        for field_name, updated_field in update_field.items():
                            old_fields[field_name] = updated_field

                    if delete_field:
                        drop_query = construct_drop_column_query(table_name, delete_field, schema_metadata.fields)
                        if drop_query:
                            cursor.execute(drop_query)
                        for deleted_field in delete_field:
                            del old_fields[deleted_field]
                        
                    schema_metadata.fields = old_fields
                    schema_metadata.save()

                    return JsonResponse({'message': f'Table {table_name} updated successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)})


# delete a table
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_table(request):
        data = json.loads(request.body)
        table_name = data.get('table_name')

        if not table_name:
            return JsonResponse({'error': 'table_name is required'})

        if not SchemaData.objects.filter(table_name=table_name).exists():
            return JsonResponse({'error': f'Table {table_name} does not exist'})

        with connection.cursor() as cursor:
            try:
                with transaction.atomic():
                    cursor.execute(f"DROP TABLE {table_name};")

                    SchemaData.objects.filter(table_name=table_name).delete()

                    return JsonResponse({'message': f'Table {table_name} deleted successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)})


# data creation for a table
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_record(request):
        data = json.loads(request.body)
        table_name = data.get('table_name')
        record_data = data.get('record_data')  

        if not table_name or not record_data:
            return JsonResponse({'error': 'table_name and record_data are required'})

        if not SchemaData.objects.filter(table_name=table_name).exists():
            return JsonResponse({'error': f'Table {table_name} does not exist'})

        with connection.cursor() as cursor:
            try:
                columns = ', '.join(record_data.keys())
                values = ', '.join([f"'{value}'" for value in record_data.values()])
                cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values});")
                return JsonResponse({'message': 'Record created successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)})

# get data
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def read_records(request):
        table_name = request.GET.get('table_name')
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort_by', 'id')
        sort_order = request.GET.get('sort_order', 'asc')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        if not table_name:
            return JsonResponse({'error': 'table_name is required'})

        if not SchemaData.objects.filter(table_name=table_name).exists():
            return JsonResponse({'error': f'Table {table_name} does not exist'})

        with connection.cursor() as cursor:
            try:
                query = f"SELECT * FROM {table_name}"

                if search_query:
                    schema_metadata = SchemaData.objects.get(table_name=table_name)
                    fields = schema_metadata.fields.keys()
                    search_conditions = [f"{field} LIKE '%{search_query}%'" for field in fields]
                    query += " WHERE " + " OR ".join(search_conditions)

                query += f" ORDER BY {sort_by} {sort_order}"

                offset = (page - 1) * page_size
                query += f" LIMIT {page_size} OFFSET {offset};"

                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                records = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return JsonResponse({'records': records})
            except Exception as e:
                return JsonResponse({'error': str(e)})

# update data
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_record(request):
        data = json.loads(request.body)
        table_name = data.get('table_name')
        record_id = data.get('record_id')
        update_data = data.get('update_data') 

        if not table_name or not record_id or not update_data:
            return JsonResponse({'error': 'table_name, record_id, and update_data are required'})

        if not SchemaData.objects.filter(table_name=table_name).exists():
            return JsonResponse({'error': f'Table {table_name} does not exist'})

        with connection.cursor() as cursor:
            try:
                set_clause = ', '.join([f"{key} = '{value}'" for key, value in update_data.items()])
                cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = {record_id};")
                return JsonResponse({'message': 'Record updated successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)})

# delete data
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_record(request):
        data = json.loads(request.body)
        table_name = data.get('table_name')
        record_id = data.get('record_id')

        if not table_name or not record_id:
            return JsonResponse({'error': 'table_name and record_id are required'})

        if not SchemaData.objects.filter(table_name=table_name).exists():
            return JsonResponse({'error': f'Table {table_name} does not exist'})

        with connection.cursor() as cursor:
            try:
                cursor.execute(f"DELETE FROM {table_name} WHERE id = {record_id};")
                return JsonResponse({'message': 'Record deleted successfully'})
            except Exception as e:
                return JsonResponse({'error': str(e)})

# import file to insert data
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def import_csv(request):
        table_name = request.POST.get('table_name')
        csv_file = request.FILES.get('csv_file')
        file_data = csv_file.read().decode('utf-8')

        if not table_name or not csv_file:
            return JsonResponse({'error': 'table_name and csv_file are required'})

        try:
            process_csv_file.delay(file_data, table_name)
            return JsonResponse({'message': 'CSV import started successfully'})
        
        except Exception as e:
            return JsonResponse({'error': f'Error processing the CSV file: {str(e)}'})
import json
from .models import SchemaData
from django.http import JsonResponse

# returns field type with length
def get_validate_field_type_length(field_config):
    ALLOWED_FIELD_TYPES = {
        "INTEGER", "VARCHAR", "TEXT", "BOOLEAN", "DATE", "TIMESTAMP", "FLOAT", "DECIMAL"
    }
    FIELDS_WITH_LENGTH_ATTRIBUTE = {
        "VARCHAR", "CHAR", "DECIMAL", "NUMERIC"
    }
    
    field_type = field_config["type"]
    field_length = field_config.get("length")

    if field_type not in ALLOWED_FIELD_TYPES:
        raise ValueError(f"Invalid field type: {field_type}")
    
    # Handle length for specific field types
    if field_type in FIELDS_WITH_LENGTH_ATTRIBUTE and field_length:
        if isinstance(field_length, int) and field_length > 0:
            field_type = f"{field_type}({field_length})"
        else:
            raise ValueError(f"Invalid length for {field_type}. Length must be a positive integer.")
    
    return field_type

# returns field default value
def get_validate_field_default_value(field_config):
     if "default" in field_config:
        default_value = field_config["default"]
        return f"DEFAULT {default_value}"  
     return ""  
 
# returns field attributes
def get_validate_field_attributes(field_config):
    attributes = []
    if field_config.get("unique"):
        attributes.append("UNIQUE")
    if field_config.get("not_null"):
        attributes.append("NOT NULL")
    
    # Check if it's a foreign key and handle cascading delete
    if field_config.get("foreign_key"):
        referenced_table = field_config.get("foreign_key")
        attributes.append(f"REFERENCES {referenced_table}")

        # Handle ON DELETE CASCADE
        if field_config.get("cascade_delete"):
            attributes.append("ON DELETE CASCADE")
    
    return " ".join(attributes)

# Function to validate fields and create their definitions
def create_field_definitions(fields):
    fieldsArr = []
    for field_name, field_config in fields.items():
        field_type_length = get_validate_field_type_length(field_config)
        field_attributes = get_validate_field_attributes(field_config)
        field_default_value = get_validate_field_default_value(field_config)
        field = f"{field_name} {field_type_length} {field_attributes} {field_default_value}"
        fieldsArr.append(field)
    return fieldsArr



# Function to construct the create table query
def construct_create_table_query(table_name, field_definitions):
    fields_sql = ", ".join(field_definitions)
    return f'CREATE TABLE "{table_name}" (id SERIAL PRIMARY KEY, {fields_sql});'

# Function to construct the alter columns query
def construct_alter_column_query(table_name, update_field):
   alter_statements = []
   for field_name, field_props in update_field.items():
        if 'type' in field_props:
            length = f"({field_props['length']})" if 'length' in field_props else ''
            alter_statements.append(f'ALTER COLUMN "{field_name}" TYPE {field_props["type"]}{length}')
        if field_props.get("not_null"):
            alter_statements.append(f'ALTER COLUMN "{field_name}" SET NOT NULL')
        else:
            alter_statements.append(f'ALTER COLUMN "{field_name}" DROP NOT NULL')
        if field_props.get("unique"):
            alter_statements.append(f'ADD CONSTRAINT {table_name}_{field_name}_unique UNIQUE ("{field_name}")')
   if alter_statements:
        return f'ALTER TABLE "{table_name}" ' + ", ".join(alter_statements) + ";"
   else:
        return ""

# Function to construct the Add columns query
def construct_Add_column_query(table_name, field_definitions):
    alter_clauses = [f"ADD COLUMN {clause}" for clause in field_definitions]
    fields_sql = ", ".join(alter_clauses)
    return f'ALTER TABLE "{table_name}" {fields_sql};'

# Function to construct the drop columns query
def construct_drop_column_query(table_name, fields, old_fields):
    drop_columns = []
    
    for field_name in fields:  # fields is a list of column names
        if field_name not in old_fields:
            return None  # Return None to signal an error outside this function
        drop_columns.append(f'DROP COLUMN "{field_name}"')

    if not drop_columns:
        return None  # Return None if there are no valid columns to drop

    return f'ALTER TABLE "{table_name}" {", ".join(drop_columns)};'

# Function to create the schema data
def save_schema_data(table_name, fields):
    SchemaData.objects.create(table_name=table_name, fields=json.dumps(fields))

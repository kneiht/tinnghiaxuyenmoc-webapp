import pandas as pd

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.apps import apps
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .forms import *
from .models.models import *
from .renders import *
from .utils import *



@login_required
def download_excel(request, model_name):
    """
    Download an Excel file with data from the specified model using pandas.
    The headers are the field verbose names, or field names if no verbose name exists.
    Uses the model's excel_columns attribute if available.
    """
    try:
        # Get the model class based on the model_name
        model_class = apps.get_model('app_dashboard', model_name)
        
        # Get the primary key field name
        pk_field = model_class._meta.pk.name
        
        # Check if the model has excel_columns defined
        if hasattr(model_class, 'excel_columns'):
            # Use the excel_columns attribute and include primary key
            fields = [pk_field] + model_class.excel_columns
        else:
            # Get all fields including primary key
            fields = [field.name for field in model_class._meta.fields]
        
        # Get verbose names for headers
        headers = []
        for field_name in fields:
            field = model_class._meta.get_field(field_name)
            headers.append(getattr(field, 'verbose_name', field_name))
        
        # Get all records from the model
        records = model_class.objects.all().values(*fields)
        
        # Create a DataFrame from the records
        df = pd.DataFrame(list(records))
        
        # If DataFrame is empty, create one with just the headers
        if df.empty and fields:
            df = pd.DataFrame(columns=fields)
        
        # Rename columns to use verbose names
        column_mapping = {fields[i]: headers[i] for i in range(len(fields))}
        df = df.rename(columns=column_mapping)
        
        # Get Vietnamese name from model's Meta if available
        model_verbose_name = getattr(model_class, 'vietnamese_name', model_name)
        
        # Create a response with Excel file
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{model_verbose_name}.xlsx"'
        
        # Write the DataFrame to Excel
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            
            # Apply some basic styling to the header row
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # Format header row
            for col_num, column in enumerate(df.columns, 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
                
            # Adjust column widths
            for col_num, column in enumerate(df.columns, 1):
                column_letter = get_column_letter(col_num)
                worksheet.column_dimensions[column_letter].width = 15
        
        return response
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@login_required
def upload_excel(request, model_name):
    """
    Upload an Excel file and save its data to the specified model using pandas.
    The Excel file should have headers matching the field verbose names or field names.
    Uses the model's excel_columns attribute if available.
    If records contain an ID that exists in the database, they will be updated instead of created.
    """
    if request.method != 'POST':
        return HttpResponse("This view only accepts POST requests", status=405)
    
    try:
        # Get the model class based on the model_name
        model_class = apps.get_model('app_dashboard', model_name)
        
        # Get the uploaded file
        excel_file = request.FILES.get('file')
        if not excel_file:
            return HttpResponse("No file uploaded", status=400)
        
        # Read the Excel file into a DataFrame
        df = pd.read_excel(excel_file)
        
        # Get the primary key field name
        pk_field = model_class._meta.pk.name
        
        # Check if the model has excel_columns defined
        if hasattr(model_class, 'excel_columns'):
            # Use the excel_columns attribute to determine which fields to include
            # Include primary key field if not already in the list
            expected_fields = model_class.excel_columns.copy()
            if pk_field not in expected_fields:
                expected_fields.append(pk_field)
        else:
            # Include all fields including primary key
            expected_fields = [field.name for field in model_class._meta.fields]
        
        # Create a mapping from verbose names to field names
        field_mapping = {}
        for field_name in expected_fields:
            field = model_class._meta.get_field(field_name)
            verbose_name = getattr(field, 'verbose_name', field_name)
            field_mapping[verbose_name] = field_name
            field_mapping[field_name] = field_name  # Also map field name to itself
        
        # Rename DataFrame columns to match model field names
        renamed_columns = {}
        for col in df.columns:
            if col in field_mapping:
                renamed_columns[col] = field_mapping[col]
        
        # Apply the renaming
        if renamed_columns:
            df = df.rename(columns=renamed_columns)
        
        # Filter to only include columns that exist in the expected fields
        valid_columns = [col for col in df.columns if col in expected_fields]
        df = df[valid_columns]
        
        # If no valid columns were found, return an error
        if not valid_columns:
            return HttpResponse("No matching fields found in the Excel file", status=400)
        
        # Process data rows
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Handle NaN values
        df = df.replace({np.nan: None})
        
        # Convert DataFrame to list of dictionaries
        records = df.to_dict('records')
        
        for record in records:
            try:
                # Check if record has primary key and if it exists in the database
                if pk_field in record and record[pk_field] is not None:
                    # Try to get the existing instance
                    try:
                        instance = model_class.objects.get(pk=record[pk_field])
                        # Update the instance with the new values
                        for field, value in record.items():
                            setattr(instance, field, value)
                        instance.save()
                        updated_count += 1
                    except model_class.DoesNotExist:
                        # If the record with this ID doesn't exist, create a new one
                        instance = model_class(**record)
                        instance.save()
                        created_count += 1
                else:
                    # Create a new instance without ID
                    if pk_field in record:
                        del record[pk_field]  # Remove None ID to let the database assign one
                    instance = model_class(**record)
                    instance.save()
                    created_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error processing record: {str(e)}")
        
        return HttpResponse(
            f"Import completed. Created: {created_count}, Updated: {updated_count}, Errors: {error_count}"
        )
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
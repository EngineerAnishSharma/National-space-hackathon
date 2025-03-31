# /app/services/import_export_service.py
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any, Optional
import pandas as pd
import io
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app.models_db import Item as DBItem, Container as DBContainer, Placement as DBPlacement, LogActionType
from app.models_api import ImportResponse, ImportErrorDetail
from .logging_service import create_log_entry
from datetime import datetime
import iso8601 # Use robust parser

def export_containers(db: Session, user_id: Optional[str] = None) -> io.BytesIO:
    """Exports the current container data as a CSV file in a BytesIO buffer."""
    containers = db.query(DBContainer).all()

    output = io.StringIO()
    # Define columns as per requirement
    columns = ['ContainerID', 'Zone', 'Width', 'Depth', 'Height']
    data = []
    for c in containers:
        data.append({
            'ContainerID': c.containerId,
            'Zone': c.zone,
            'Width': c.width,
            'Depth': c.depth,
            'Height': c.height
        })

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output, index=False, lineterminator='\n')  # Use lineterminator for consistency

    # Log export action
    create_log_entry(
        db=db,
        actionType=LogActionType.EXPORT,
        userId=user_id,
        details={"exportType": "containers", "containerCount": len(containers)}
    )
    try:
        db.commit()  # Commit log
    except Exception as e:
        db.rollback()
        print(f"Error committing export log: {e}")  # Log error but still return data

    # Return as BytesIO for Flask send_file
    return io.BytesIO(output.getvalue().encode('utf-8'))

def export_items(db: Session, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Exports the current item data as JSON."""
    items = db.query(DBItem).all()

    data = []
    for item in items:
        data.append({
            'ItemID': item.itemId,
            'Name': item.name,
            'Width': item.width,
            'Depth': item.depth,
            'Height': item.height,
            'Mass': item.mass,
            'Priority': item.priority,
            'ExpiryDate': item.expiryDate.isoformat() if item.expiryDate else None,
            'UsageLimit': item.usageLimit,
            'PreferredZone': item.preferredZone
        })

    # Log export action
    create_log_entry(
        db=db,
        actionType=LogActionType.EXPORT,
        userId=user_id,
        details={"exportType": "items", "itemCount": len(items)}
    )
    try:
        db.commit()  # Commit log
    except Exception as e:
        db.rollback()
        print(f"Error committing export log: {e}")  # Log error but still return data

    return data


def import_items_from_csv(db: Session, file: FileStorage, user_id: Optional[str] = None) -> ImportResponse:
    """Imports item data from a CSV file."""
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.csv'):
        return ImportResponse(success=False, errors=[ImportErrorDetail(message="Invalid file type. Please upload a CSV file.")])

    items_imported_count = 0
    errors: List[ImportErrorDetail] = []

    try:
        # Read CSV using pandas - handle potential encoding issues
        try:
            df = pd.read_csv(file.stream, encoding='utf-8')
        except UnicodeDecodeError:
             file.stream.seek(0) # Reset stream position
             df = pd.read_csv(file.stream, encoding='latin-1') # Try alternative encoding


        # --- Define Expected Columns (Case Insensitive) ---
        # Adjust these based on the exact expected CSV format
        required_columns = {
            'itemid': 'itemId', 'name': 'name', 'width': 'width', 'depth': 'depth',
            'height': 'height', 'mass': 'mass', 'priority': 'priority'
        }
        optional_columns = {
            'expirydate': 'expiryDate', 'usagelimit': 'usageLimit', 'preferredzone': 'preferredZone'
        }
        df.columns = df.columns.str.lower().str.replace(' ', '').str.replace('_', '') # Normalize column names

        missing_req = [col for col in required_columns.keys() if col not in df.columns]
        if missing_req:
            errors.append(ImportErrorDetail(message=f"Missing required columns: {', '.join(missing_req)}"))
            return ImportResponse(success=False, errors=errors)


        # --- Iterate through rows and import ---
        for index, row in df.iterrows():
            row_num = index + 2 # Account for header and 0-based index
            item_data = {}
            current_row_errors = []

            # Map required columns
            for csv_col, model_field in required_columns.items():
                 item_data[model_field] = row.get(csv_col)

            # Map optional columns
            for csv_col, model_field in optional_columns.items():
                 if csv_col in df.columns:
                     item_data[model_field] = row.get(csv_col)

            # --- Data Type Conversion and Validation ---
            try:
                item_data['itemId'] = str(item_data['itemId'])
                item_data['name'] = str(item_data['name'])
                item_data['width'] = float(item_data['width'])
                item_data['depth'] = float(item_data['depth'])
                item_data['height'] = float(item_data['height'])
                item_data['mass'] = float(item_data['mass'])
                item_data['priority'] = int(item_data['priority'])

                if 'usageLimit' in item_data and pd.notna(item_data['usageLimit']):
                     try:
                         item_data['usageLimit'] = int(float(item_data['usageLimit'])) # Handle potential float like '10.0'
                     except (ValueError, TypeError):
                         current_row_errors.append(f"Invalid format for usageLimit ('{item_data['usageLimit']}')")
                         item_data['usageLimit'] = None # Skip if invalid
                else:
                     item_data['usageLimit'] = None


                if 'expiryDate' in item_data and pd.notna(item_data['expiryDate']):
                     try:
                        # Attempt parsing various common date formats or ISO 8601
                         if isinstance(item_data['expiryDate'], datetime):
                              item_data['expiryDate'] = item_data['expiryDate'] # Already datetime
                         else:
                             item_data['expiryDate'] = iso8601.parse_date(str(item_data['expiryDate']))
                     except (ValueError, TypeError, iso8601.ParseError):
                        current_row_errors.append(f"Invalid date format for expiryDate ('{item_data['expiryDate']}')")
                        item_data['expiryDate'] = None # Skip if invalid
                else:
                    item_data['expiryDate'] = None

                if 'preferredZone' in item_data and pd.notna(item_data['preferredZone']):
                     item_data['preferredZone'] = str(item_data['preferredZone'])
                else:
                     item_data['preferredZone'] = None


                # --- Check for mandatory field presence after potential nulls ---
                if not all(k in item_data and pd.notna(item_data.get(k)) for k in required_columns.values()):
                    current_row_errors.append("Missing value in one or more required columns")


                # TODO: Add more specific validations (e.g., priority range, positive dimensions/mass)


            except (ValueError, TypeError) as e:
                 current_row_errors.append(f"Data type error: {e}")


            if current_row_errors:
                 errors.append(ImportErrorDetail(row=row_num, message="; ".join(current_row_errors)))
                 continue # Skip this row

            # --- Upsert Logic (Update if exists, else Create) ---
            existing_item = db.query(DBItem).filter(DBItem.itemId == item_data['itemId']).first()
            if existing_item:
                 # Update existing item (be careful what you update)
                 existing_item.name = item_data['name']
                 existing_item.width = item_data['width']
                 existing_item.depth = item_data['depth']
                 existing_item.height = item_data['height']
                 existing_item.mass = item_data['mass']
                 existing_item.priority = item_data['priority']
                 existing_item.expiryDate = item_data.get('expiryDate')
                 existing_item.usageLimit = item_data.get('usageLimit')
                 existing_item.preferredZone = item_data.get('preferredZone')
                 # Should status or currentUses be reset on import? Assume not.
                 print(f"Updated item: {item_data['itemId']}")
            else:
                 # Create new item
                 new_item = DBItem(**item_data)
                 db.add(new_item)
                 items_imported_count += 1
                 print(f"Created new item: {item_data['itemId']}")

        # --- Commit changes after processing all rows ---
        if items_imported_count > 0 or any(db.dirty): # Check if there's anything to commit
             try:
                 db.commit()
             except Exception as e:
                 db.rollback()
                 errors.append(ImportErrorDetail(message=f"Database commit failed: {e}"))
                 # Mark overall success as false if commit fails
                 success_status = False
             else:
                  success_status = len(errors) == 0 # Success only if no errors occurred
        else:
             success_status = len(errors) == 0 # Success if no errors, even if nothing imported

        # Log the import action
        create_log_entry(
            db=db,
            actionType=LogActionType.IMPORT,
            userId=user_id,
            details={
                "fileType": "items",
                "fileName": filename,
                "count": items_imported_count,
                "errors": len(errors)
            }
        )
        db.commit() # Commit the log entry


        return ImportResponse(success=success_status, itemsImported=items_imported_count, errors=errors)


    except pd.errors.ParserError as e:
        errors.append(ImportErrorDetail(message=f"CSV Parsing Error: {e}"))
        return ImportResponse(success=False, errors=errors)
    except Exception as e:
        db.rollback() # Rollback any partial additions
        errors.append(ImportErrorDetail(message=f"An unexpected error occurred: {e}"))
        # Log the error if possible
        try:
            create_log_entry(db, LogActionType.SYSTEM_ERROR, userId=user_id, details={"error": f"Item Import Failed: {e}", "fileName": filename})
            db.commit()
        except:
            db.rollback() # Rollback log commit if it fails
        return ImportResponse(success=False, errors=errors)


def import_containers_from_csv(db: Session, file: FileStorage, user_id: Optional[str] = None) -> ImportResponse:
    """Imports container data from a CSV file."""
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.csv'):
        return ImportResponse(success=False, errors=[ImportErrorDetail(message="Invalid file type. Please upload a CSV file.")])

    containers_imported_count = 0
    errors: List[ImportErrorDetail] = []

    try:
        try:
            df = pd.read_csv(file.stream, encoding='utf-8')
        except UnicodeDecodeError:
            file.stream.seek(0)
            df = pd.read_csv(file.stream, encoding='latin-1')

        # --- Define Expected Columns (Case Insensitive) ---
        required_columns = {'containerid': 'containerId', 'zone': 'zone', 'width': 'width', 'depth': 'depth', 'height': 'height'}
        df.columns = df.columns.str.lower().str.replace(' ', '').str.replace('_', '') # Normalize

        missing_req = [col for col in required_columns.keys() if col not in df.columns]
        if missing_req:
            errors.append(ImportErrorDetail(message=f"Missing required columns: {', '.join(missing_req)}"))
            return ImportResponse(success=False, errors=errors)

        # --- Iterate and import ---
        for index, row in df.iterrows():
            row_num = index + 2
            cont_data = {}
            current_row_errors = []

            for csv_col, model_field in required_columns.items():
                 cont_data[model_field] = row.get(csv_col)

            # --- Data Type Conversion and Validation ---
            try:
                cont_data['containerId'] = str(cont_data['containerId'])
                cont_data['zone'] = str(cont_data['zone'])
                cont_data['width'] = float(cont_data['width'])
                cont_data['depth'] = float(cont_data['depth'])
                cont_data['height'] = float(cont_data['height'])

                if not all(k in cont_data and pd.notna(cont_data.get(k)) for k in required_columns.values()):
                     current_row_errors.append("Missing value in one or more required columns")
                # TODO: Add more specific validations (positive dimensions)

            except (ValueError, TypeError) as e:
                 current_row_errors.append(f"Data type error: {e}")

            if current_row_errors:
                 errors.append(ImportErrorDetail(row=row_num, message="; ".join(current_row_errors)))
                 continue

            # --- Upsert Logic ---
            existing_cont = db.query(DBContainer).filter(DBContainer.containerId == cont_data['containerId']).first()
            if existing_cont:
                 # Update existing container
                 existing_cont.zone = cont_data['zone']
                 existing_cont.width = cont_data['width']
                 existing_cont.depth = cont_data['depth']
                 existing_cont.height = cont_data['height']
                 print(f"Updated container: {cont_data['containerId']}")
            else:
                 # Create new container
                 new_cont = DBContainer(**cont_data)
                 db.add(new_cont)
                 containers_imported_count += 1
                 print(f"Created new container: {cont_data['containerId']}")


        # --- Commit changes ---
        if containers_imported_count > 0 or any(db.dirty):
            try:
                 db.commit()
            except Exception as e:
                 db.rollback()
                 errors.append(ImportErrorDetail(message=f"Database commit failed: {e}"))
                 success_status = False
            else:
                 success_status = len(errors) == 0
        else:
             success_status = len(errors) == 0


        # Log import action
        create_log_entry(
            db=db,
            actionType=LogActionType.IMPORT,
            userId=user_id,
            details={
                "fileType": "containers",
                "fileName": filename,
                "count": containers_imported_count,
                "errors": len(errors)
            }
        )
        db.commit() # Commit log


        return ImportResponse(success=success_status, containersImported=containers_imported_count, errors=errors)

    except pd.errors.ParserError as e:
        errors.append(ImportErrorDetail(message=f"CSV Parsing Error: {e}"))
        return ImportResponse(success=False, errors=errors)
    except Exception as e:
        db.rollback()
        errors.append(ImportErrorDetail(message=f"An unexpected error occurred: {e}"))
        try:
             create_log_entry(db, LogActionType.SYSTEM_ERROR, userId=user_id, details={"error": f"Container Import Failed: {e}", "fileName": filename})
             db.commit()
        except:
             db.rollback()
        return ImportResponse(success=False, errors=errors)


def export_current_arrangement(db: Session, user_id: Optional[str] = None) -> io.BytesIO:
    """Exports the current item placements as a CSV file in a BytesIO buffer."""
    placements = db.query(DBPlacement).options(joinedload(DBPlacement.item)).all()

    output = io.StringIO()
    # Define columns as per requirement
    columns = ['ItemID', 'ContainerID', 'Coordinates(W1,D1,H1)', 'Coordinates(W2,D2,H2)']
    data = []
    for p in placements:
         # Format coordinates as required string
         coord1 = f"({p.start_w},{p.start_d},{p.start_h})"
         coord2 = f"({p.end_w},{p.end_d},{p.end_h})"
         data.append({
             'ItemID': p.itemId_fk,
             'ContainerID': p.containerId_fk,
             'Coordinates(W1,D1,H1)': coord1,
             'Coordinates(W2,D2,H2)': coord2
         })

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output, index=False, lineterminator='\n') # Use lineterminator for consistency

    # Log export action
    create_log_entry(
        db=db,
        actionType=LogActionType.EXPORT,
        userId=user_id,
        details={"exportType": "arrangement", "itemCount": len(placements)}
    )
    try:
        db.commit() # Commit log
    except Exception as e:
        db.rollback()
        print(f"Error committing export log: {e}") # Log error but still return data


    # Return as BytesIO for Flask send_file
    return io.BytesIO(output.getvalue().encode('utf-8'))
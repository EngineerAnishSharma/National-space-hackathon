# app/services/import_export_service.py
import csv
from sqlalchemy.orm import Session
from app.database import Item as ItemDB, Container as ContainerDB  # Import SQLAlchemy models
from app.models import Item, Container #Import Model file to create those models
from datetime import datetime
from io import StringIO
from sqlalchemy.exc import IntegrityError

class ImportExportService:
    def __init__(self):
        pass

    def import_items_from_csv(self, csv_file: str, db: Session):
        """Imports items from a CSV file into the database."""
        items_imported = 0
        errors = []

        try:
            csv_data = StringIO(csv_file)
            reader = csv.DictReader(csv_data)

            for i, row in enumerate(reader):
                try:
                    item_id = row['Item ID']
                    name = row['Name']
                    width = float(row['Width'])
                    depth = float(row['Depth'])
                    height = float(row['Height'])
                    mass = float(row['Mass'])
                    priority = int(row['Priority'])
                    preferred_zone = row['Preferred Zone']

                    # Handle optional fields
                    expiry_date_str = row.get('Expiry Date')
                    # Updated expiry date processing
                    if expiry_date_str and expiry_date_str not in ('N/A', '#'*10):
                        try:
                            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                        except ValueError:
                            expiry_date = None  # Or handle the error as you see fit
                    else:
                        expiry_date = None  # Set to None if 'N/A' or '##########'

                    usage_limit_str = row.get('Usage Limit')
                    usage_limit = int(usage_limit_str) if usage_limit_str else None

                    #Create Item object.
                    item_data = {
                        "itemId": item_id,
                        "name": name,
                        "width": width,
                        "depth": depth,
                        "height": height,
                        "mass": mass,
                        "priority": priority,
                        "expiryDate": expiry_date,
                        "usageLimit": usage_limit,
                        "preferredZone": preferred_zone,
                    }
                    item = Item(**item_data)
                    #Create Item object
                    item_db = ItemDB(
                        itemId=item.itemId,
                        name=item.name,
                        width=item.width,
                        depth=item.depth,
                        height=item.height,
                        mass=item.mass,
                        priority=item.priority,
                        expiryDate=item.expiryDate,
                        usageLimit=item.usageLimit,
                        preferredZone=item.preferredZone,
                    )

                    # Check if the item already exists before adding
                    existing_item = db.query(ItemDB).filter(ItemDB.itemId == item.itemId).first()
                    if not existing_item:
                        db.add(item_db)
                        items_imported += 1

                except ValueError as e:
                    errors.append({"row": i + 2, "message": f"Invalid data format: {e}"})
                except KeyError as e:
                    errors.append({"row": i + 2, "message": f"Missing column: {e}"})
                except IntegrityError as e:
                    db.rollback()
                    errors.append({"row": i + 2, "message": f"IntegrityError: {e}"})
                    print(f"Skipping duplicate item with ID: {item.itemId}")

            db.commit()
            return {"success": True, "itemsImported": items_imported, "errors": errors}
        except Exception as e:
            errors.append({"row": 0, "message": f"File processing error: {e}"})
            return {"success": False, "itemsImported": 0, "errors": errors}

    def import_containers_from_csv(self, csv_file: str, db: Session):
        """Imports containers from a CSV file into the database."""
        containers_imported = 0
        errors = []

        try:
            csv_data = StringIO(csv_file)
            reader = csv.DictReader(csv_data)

            for i, row in enumerate(reader):
                try:
                    zone = row['Zone']
                    container_id = row['Container ID']
                    width = float(row['Width'])
                    depth = float(row['Depth'])
                    height = float(row['Height'])

                    # Validate using Pydantic model
                    container_data = {
                        "zone": zone,
                        "containerId": container_id,
                        "width": width,
                        "depth": depth,
                        "height": height,
                    }
                    container = Container(**container_data)  # Validate data with Pydantic Model

                    # Create and add to the database
                    container_db = ContainerDB(
                        containerId=container.containerId,
                        zone=container.zone,
                        width=container.width,
                        depth=container.depth,
                        height=container.height,
                    )
                    db.add(container_db)
                    containers_imported += 1

                except ValueError as e:
                    errors.append({"row": i + 2, "message": f"Invalid data format: {e}"})
                except KeyError as e:
                    errors.append({"row": i + 2, "message": f"Missing column: {e}"})
                except IntegrityError as e:
                    db.rollback()
                    errors.append({"row": i + 2, "message": f"IntegrityError: {e}"})
                    print(f"Skipping duplicate container with ID: {container.containerId}")

            db.commit()
            return {"success": True, "containersImported": containers_imported, "errors": errors}
        except Exception as e:
            errors.append({"row": 0, "message": f"File processing error: {e}"})
            return {"success": False, "containersImported": 0, "errors": errors}
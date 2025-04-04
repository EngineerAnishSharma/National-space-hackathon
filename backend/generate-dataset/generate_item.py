import pandas as pd
import numpy as np
from random import randint, choice, uniform
from datetime import datetime, timedelta
from sample_data import expanded_items_dict
import json

# Generate 2000 items using the updated dictionary with multiple possible locations

num_items = 2000
data = []
json_data = []  # List to store items for JSON output

for start_id in range(1, num_items + 1):
    item_id = f"{start_id:06d}"  # 6-digit ID
    item, possible_zones = choice(list(expanded_items_dict.items()))  # Randomly pick an item and its zones
    
    # Assign one or two preferred zones from the possible locations
    preferred_zone = choice(possible_zones)

    # Size and mass adjustments based on item type
    if "Cylinder" in item or "Tank" in item:
        width = round(uniform(15.0, 30.0), 1)
        depth = round(uniform(15.0, 30.0), 1)
        height = round(uniform(40.0, 100.0), 1)
        mass = round(uniform(10.0, 50.0), 1)
    elif "Panel" in item:
        width = round(uniform(40.0, 100.0), 1)
        depth = round(uniform(40.0, 100.0), 1)
        height = round(uniform(1.0, 5.0), 1)
        mass = round(uniform(5.0, 20.0), 1)
    elif "Kit" in item or "Packet" in item or "Sample" in item:
        width = round(uniform(10.0, 30.0), 1)
        depth = round(uniform(10.0, 30.0), 1)
        height = round(uniform(10.0, 30.0), 1)
        mass = round(uniform(1.0, 10.0), 1)
    else:
        width = round(uniform(10.0, 50.0), 1)
        depth = round(uniform(10.0, 50.0), 1)
        height = round(uniform(10.0, 50.0), 1)
        mass = round((width * depth * height) / 2000, 2)  # More precise mass calculation

    priority = randint(1, 100)

    # Expiry date only for perishable or medical items
    if "Food" in item or "Medical" in item or "Antibiotic" in item:
        expiry_date = (datetime.today() + timedelta(days=randint(30, 730))).strftime('%Y-%m-%dT00:00:00Z')  # ISO 8601 format
    else:
        expiry_date = None  # or null

    # Usage limit relevant to item type
    if "Kit" in item or "Packet" in item or "Food" in item or "Medical" in item:
        usage_limit = randint(1, 100)
    elif "Battery" in item or "Filter" in item or "Scrubber" in item:
        usage_limit = randint(100, 1000)
    else:
        usage_limit = randint(1, 5000)

    data.append([item_id, item.replace(" ", "_"), width, depth, height, mass, priority, expiry_date, usage_limit, preferred_zone])

    # Create JSON entry
    json_item = {
        "itemId": item_id,
        "name": item.replace(" ", "_"),
        "width": width,
        "depth": depth,
        "height": height,
        "mass": mass,
        "priority": priority,
        "expiryDate": expiry_date,
        "usageLimit": usage_limit,
        "preferredZone": preferred_zone
    }
    json_data.append(json_item)

# Create DataFrame with 6-digit IDs and multiple zones
df_final = pd.DataFrame(data, columns=[
    "item_id", "name", "width_cm", "depth_cm", "height_cm", 
    "mass_kg", "priority", "expiry_date", "usage_limit", "preferred_zone"
])

csv_final_path = "input_items.csv"
df_final.to_csv(csv_final_path, index=False)
print(f"CSV file saved to: {csv_final_path}")

# Create JSON file
json_output = {"items": json_data}
json_file_path = "input_items.json"
with open(json_file_path, 'w') as outfile:
    json.dump(json_output, outfile, indent=4)

print(f"JSON file saved to: {json_file_path}")
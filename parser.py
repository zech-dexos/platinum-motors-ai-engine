import csv
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from pydantic import ValidationError
from inventory import Vehicle, VehicleStatus
import requests

def parse_csv(filepath: str) -> List[Vehicle]:
    """Parse local CSV inventory feed."""
    vehicles = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Map row keys to model fields, handling empty strings as None
                    clean_row = {k: v if v != '' else None for k, v in row.items()}
                    
                    # Convert specific fields to correct types
                    if clean_row.get('year'): clean_row['year'] = int(clean_row['year'])
                    if clean_row.get('price'): clean_row['price'] = float(clean_row['price'])
                    if clean_row.get('mileage'): clean_row['mileage'] = int(clean_row['mileage'])
                    
                    # Handle image_urls parsing if it's a comma-separated string
                    if clean_row.get('image_urls'):
                        clean_row['image_urls'] = [url.strip() for url in clean_row['image_urls'].split(',')]
                    
                    vehicles.append(Vehicle(**clean_row))
                except ValidationError as e:
                    print(f"Validation error for row {row}: {e}")
                except Exception as e:
                     print(f"Error parsing row {row}: {e}")
    except FileNotFoundError:
        print(f"CSV file not found: {filepath}")
    return vehicles

def parse_json(filepath: str) -> List[Vehicle]:
    """Parse local JSON inventory feed."""
    vehicles = []
    try:
         with open(filepath, 'r', encoding='utf-8') as f:
             data = json.load(f)
             for item in data:
                 try:
                     vehicles.append(Vehicle(**item))
                 except ValidationError as e:
                     print(f"Validation error for item {item.get('vin', 'UNKNOWN')}: {e}")
    except FileNotFoundError:
         print(f"JSON file not found: {filepath}")
    except json.JSONDecodeError:
         print(f"Invalid JSON in file: {filepath}")
    return vehicles

def parse_xml(filepath: str) -> List[Vehicle]:
    """Parse local XML inventory feed.
    Assumes standard structure <vehicles><vehicle>...</vehicle></vehicles>
    """
    vehicles = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for vehicle_node in root.findall('vehicle'):
            vehicle_data = {}
            for child in vehicle_node:
                if child.tag == 'image_urls':
                    vehicle_data['image_urls'] = [url.text for url in child.findall('url')]
                else:
                    vehicle_data[child.tag] = child.text
            
            try:
                # Type conversions
                if vehicle_data.get('year'): vehicle_data['year'] = int(vehicle_data['year'])
                if vehicle_data.get('price'): vehicle_data['price'] = float(vehicle_data['price'])
                if vehicle_data.get('mileage'): vehicle_data['mileage'] = int(vehicle_data['mileage'])
                
                vehicles.append(Vehicle(**vehicle_data))
            except ValidationError as e:
                print(f"Validation error for XML vehicle {vehicle_data.get('vin', 'UNKNOWN')}: {e}")
    except FileNotFoundError:
        print(f"XML file not found: {filepath}")
    except ET.ParseError:
        print(f"XML parsing error in file: {filepath}")
    return vehicles

def parse_remote_json(url: str) -> List[Vehicle]:
    """Parse remote JSON inventory feed."""
    vehicles = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data:
            try:
                vehicles.append(Vehicle(**item))
            except ValidationError as e:
                print(f"Validation error for remote item {item.get('vin', 'UNKNOWN')}: {e}")
    except requests.RequestException as e:
        print(f"Error fetching remote JSON from {url}: {e}")
    return vehicles

def manual_intake(raw_data: Dict[str, Any]) -> Optional[Vehicle]:
    """
    Manual intake for new vehicle arrivals (specifically 'Coming Soon').
    Accepts basic raw text/specs.
    """
    try:
        # Default to COMING_SOON if not specified
        if 'status' not in raw_data:
            raw_data['status'] = VehicleStatus.COMING_SOON
        
        vehicle = Vehicle(**raw_data)
        return vehicle
    except ValidationError as e:
        print(f"Validation error during manual intake: {e}")
        return None

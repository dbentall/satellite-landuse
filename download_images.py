import ee
from datetime import timedelta
from typing import List
from datetime import datetime
from pathlib import Path
import urllib.request
import json
import sys

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def select_and_download_images(grid: List[float], output_parent_folder: Path):
    # Ensure output parent directory exists
    output_parent_folder.mkdir(parents=True, exist_ok=True)
    
    # Find the first and last available dates in the dataset
    collection = (ee.ImageCollection('COPERNICUS/S2')
                  .filterBounds(ee.Geometry.Polygon(grid)))
    
    print(collection.size().getInfo())
    try:
        start_date = ee.Date(collection.first().get('system:time_start')).getInfo()
        print(start_date)
        end_date = ee.Date(collection.sort('system:time_end', False).first().get('system:time_end')).getInfo()
        print(end_date)
    except:
        print("No images available for the given grid.")
        return
    
    # Convert timestamps to datetime objects
    start_date = datetime.utcfromtimestamp(start_date['value']/1000.0)
    end_date = datetime.utcfromtimestamp(end_date['value']/1000.0)
    
    # Loop through years from start to end
    current_year = start_date.year
    while current_year < end_date.year:
        # Define the dates for Oct of current year, and Jan & Mar of the next year
        oct_date = datetime(current_year, 10, 1)
        jan_date = datetime(current_year + 1, 1, 1)
        mar_date = datetime(current_year + 1, 3, 1)
        
        # Check if this group is within the dataset range
        if oct_date >= start_date and mar_date + timedelta(days=30) <= end_date:
            # Create a folder for this group
            group_folder_name = f'{current_year}_{current_year + 1}_Oct_Jan_Mar'
            group_folder_path = output_parent_folder / group_folder_name
            group_folder_path.mkdir(parents=True, exist_ok=True)
            
            # List to hold the specific months in the group
            months_in_group = [oct_date, jan_date, mar_date]
            
            for date in months_in_group:
                end_date_obj = date + timedelta(days=30)
                
                # Retrieve images for a 1-month interval
                print(grid)
                collection = (ee.ImageCollection('COPERNICUS/S2')
                              .filterBounds(ee.Geometry.Polygon(grid))
                              .filterDate(ee.Date(date), ee.Date(end_date_obj))
                              .sort('CLOUDY_PIXEL_PERCENTAGE'))
                
                # Retrieve the first image (with the lowest cloud pixel percentage)
                image = ee.Image(collection.first())
                
                # Select the specified bands from the image
                bands = ['B2', 'B3', 'B4', 'B8A', 'B11', 'B12']
                image = image.select(bands)
                
                # Get the download URL for the given image, rectangle, and bands
                download_url = image.getDownloadURL({
                    'scale': 10,
                    'crs': 'EPSG:4326',  # WGS84 projection
                    'region': ee.Geometry.Polygon(grid).getInfo()['coordinates']
                })
                
                # Build the file path for downloading the image
                month = date.strftime('%b')
                file_name = f'{current_year}_{month}_image.zip'
                output_file_path = group_folder_path / file_name
                
                # Download the image using Python
                urllib.request.urlretrieve(download_url, output_file_path)
                print("Image downloaded to", output_file_path)
                
        # Move to the next year
        current_year += 1

if __name__ == "__main__":
    # Check if any argument is provided
    if len(sys.argv) < 2:
        print("Please provide an argument of a collection of coordinates in json format.")
        sys.exit(1)

    json_path = Path(sys.argv[1])

    # Check if the provided file has a .json extension and exists
    if not json_path.suffix == ".json" or not json_path.exists():
        print("Invalid JSON file location provided.")
        sys.exit(1)
    
    cords_dict = load_json(json_path)
    
    # Initialize the Google Earth Engine
    ee.Initialize()


    for name, grid in coords_dict.items():
        output_parent_folder = Path(f'downloaded_images/{name}')
        Path.mkdir(output_parent_folder, parents=True, exist_ok=True)
        print(grid)
        select_and_download_images(grid, output_parent_folder)
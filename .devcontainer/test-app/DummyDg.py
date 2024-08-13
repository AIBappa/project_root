import os
import pandas as pd
import random
import string
import logging
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, LargeBinary
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import Geometry


# Lists of common Indian first names and surnames
first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Mohan", "Radheshyam", "Jignesh", "Shakti", "Arya", "Amrut", "Romesh", "Mayank"]
surnames = ["Sharma", "Verma", "Gupta", "Mehta", "Patel", "Reddy", "Chauhan", "Rajput", "Singh", "Kumar", "Jadhav", "Chavan", "Dhargalkar", "Netravalkar", "Joshi", "Jagtap", "Nalawade", "Nimbalkar", "Bhosale"]

# Function to generate a random mobile number
def generate_mobile():
    return "9" + ''.join(random.choices(string.digits, k=9))

# Function to generate a random email ID
def generate_email(name):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "aol.com", "protonmail.com" ]
    return f"{name.lower().replace(' ', '')}@{random.choice(domains)}"

# Function to generate a random address in India
def generate_address():
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune", "Jaipur", "Surat"]
    return f"{random.randint(1, 500)}, {random.choice(cities)}"

# Function to generate a random GPS location within India
def generate_gps():
    lat = round(random.uniform(8.4, 37.6), 6)
    lon = round(random.uniform(68.7, 97.25), 6)
    return f"{lat}, {lon}"

# Generate 1000 dummy records
data = []
for _ in range(100):
    first_name = random.choice(first_names)
    surname = random.choice(surnames)
    full_name = f"{first_name} {surname}"
    mobile = generate_mobile()
    address = generate_address()
    gps = generate_gps()
    email = generate_email(full_name)
    data.append([full_name, mobile, address, gps, email])

# Create a DataFrame
df = pd.DataFrame(data, columns=["Name", "Mobile", "Address", "GPS_Location", "Email"])

# Create a GeoDataFrame
df[['latitude', 'longitude']] = df['GPS_Location'].str.split(',', expand=True)
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)

# Create a geometry column using longitude and latitude
geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# Convert the geometry to WKT/WKB, for WKT, change all WKB instances to WKT.
gdf['geometry_wkt'] = gdf['geometry'].apply(lambda geom: geom.wkt)

# Verify the geometry column
print(gdf['geometry_wkt'])

# Convert the geometry to WKB and WKT (Well-Known Text)
#df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
#df['wkb_geometry'] = df['geometry'].apply(lambda geom: wkb_dumps(geom, hex=True))

# Get the current date and time
now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

# Create output directory if it does not exist
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save to Excel file in the output directory
file_name = os.path.join(output_dir, f"dummy_farmers_data_{now.strftime('%Y%m%d_%H%M%S')}.xlsx")
gdf.to_excel(file_name, index=False, sheet_name='Sheet1')

# Add the timestamp to a new sheet in the Excel file
with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    pd.DataFrame([["Data saved on:", current_time]]).to_excel(writer, sheet_name='Timestamp', header=False, index=False)

print(f"Data saved to {file_name}")

#####################Save to Excel Completed ##############

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup engine and metadata
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
metadata = MetaData()

# Define table schema
cosellwkt_table = Table('cosellwkt', metadata,
    Column('id', Integer, primary_key=True),
    Column('Name', String),
    Column('Mobile', String),
    Column('Address', String),
    Column('GPS_Location', String),
    Column('Email', String),
    Column('latitude', Float),
    Column('longitude', Float),
    #Column('geometry_wkb', LargeBinary)  # Column to store WKB representation of geometry
    Column('geometry_wkt', Geometry(geometry_type='POINT', srid=4326))
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Convert DataFrame rows to a list of dictionaries
# data_dicts = gdf.to_dict(orient='records')

# Prepare data for insertion by including the geometry_wkb column
data_dicts = gdf.drop(columns='geometry').to_dict(orient='records')

# Insert data into the table
with engine.connect() as conn:
    for record in data_dicts:
        insert_query = cosellwkt_table.insert().values(
            Name=record['Name'],
            Mobile=record['Mobile'],
            Address=record['Address'],
            GPS_Location=record['GPS_Location'],
            Email=record['Email'],
            latitude=record['latitude'],
            longitude=record['longitude'],
            geometry_wkt=f"SRID=4326;{record['geometry_wkt']}"  # Using WKT format here
        )
        try:
            conn.execute(insert_query)
            conn.commit()
            print("Data inserted successfully.")
        except Exception as e:
            print(f"Error while inserting data: {e}")
        

####################New and Append to Farmers Table Completed###################
# Issue noted- Schema difference in table rejects data input to table, schema check needed####
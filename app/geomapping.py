import pandas as pd
# from opencage.geocoder import OpenCageGeocode
import time
from math import radians, cos, sin, sqrt, atan2
import re


# major and building list
majors_to_buildings = {
    "Computer Science": ["Gates Dell Complex (GDC)", "Peter O'Donnell Jr. Building (POB)"],
    "Electrical and Computer Engineering": ["Engineering Education and Research Center (EER)",  "Engineering Teaching Center (ETC)", "Ernest Cockrell Jr. Hall (ECJ)"],
    "Mechanical Engineering": ["Engineering Teaching Center (ETC)", "Engineering Education and Research Center (EER)"],
    "Biomedical Engineering": ["Biomedical Engineering Building (BME)", "Engineering Education and Research Center (EER)"],
    "Chemical Engineering": ["Norman Hackerman Building (NHB)", "Engineering Education and Research Center (EER)"],
    "Aerospace Engineering": ["Aerospace Engineering Building (ASE)", "Engineering Education and Research Center (EER)"],
    "Civil Engineering": ["Ernest Cockrell Jr. Hall (ECJ)"],
    "Architectural Engineering": ["Goldsmith Hall (GOL)", "Battle Hall (BTL)"],
    "Architecture": ["Goldsmith Hall (GOL)", "Sutton Hall (SUT)", "Battle Hall (BTL)"],
    "Business (McCombs)": ["McCombs School of Business (CBA)", "Graduate Business Building (GSB)"],
    "Finance": ["McCombs School of Business (CBA)"],
    "Marketing": ["McCombs School of Business (CBA)"],
    "Management Information Systems (MIS)": ["McCombs School of Business (CBA)"],
    "Accounting": ["McCombs School of Business (CBA)"],
    "Economics": ["College of Liberal Arts Building (CLA)", "BRB Building"],
    "Government (Political Science)": ["College of Liberal Arts Building (CLA)", "Burdine Hall (BUR)"],
    "Psychology": ["Seay Building (SEA)"],
    "Biology": ["Biological Laboratories (BIO)", "Norman Hackerman Building (NHB)", "Welch Hall (WEL)"],
    "Chemistry": ["Welch Hall (WEL)", "Norman Hackerman Building (NHB)"],
    "Physics": ["Robert Lee Moore Hall (RLM)", "Painter Hall (PAI)"],
    "Mathematics": ["Robert Lee Moore Hall (RLM)", "Painter Hall (PAI)"],
    "Statistics and Data Science": ["Robert Lee Moore Hall (RLM)", "Gates Dell Complex (GDC)"],
    "English": ["Parlin Hall (PAR)", "Benedict Hall (BEN)"],
    "History": ["Garison Hall (GAR)", "Benedict Hall (BEN)"],
    "Philosophy": ["Waggener Hall (WAG)"],
    "Sociology": ["Burdene Hall (BUR)"],
    "Anthropology": ["SAC Building", "Patton Hall (RLP)"],
    "Radio-Television-Film (RTF)": ["Moody College of Communication (CMA)", "Belo Center for New Media (BMC)"],
    "Journalism": ["Belo Center for New Media (BMC)"],
    "Public Relations and Advertising": ["Moody College of Communication (CMA)", "Belo Center for New Media (BMC)"],
    "Geosciences (Geology)": ["Jackson Geological Sciences Building (JGB)"],
    "Environmental Science": ["Jackson Geological Sciences Building (JGB)", "Welch Hall (WEL)"],
    "Geography": ["RLP (Patton Hall)"],
    "Fine Arts (Art, Theatre, Dance)": ["Fine Arts Building (ART)", "Winship Drama Building (WIN)"],
    "Music": ["Butler School of Music (MRH)"],
    "Education": ["Sanchez Building (SZB)"],
    "Social Work": ["Steve Hicks School of Social Work Building (SSW)"],
    "Nursing": ["School of Nursing (NUR)"],
    "Public Health": ["Dell Medical School (DMS)"],
    "Law": ["Townes Hall (TNH)"],
    "Pharmacy": ["Pharmacy Building (PHR)"],
    "Engineering Honors Program (EHP)": ["Engineering Teaching Center (ETC)", "EER"],
    "Liberal Arts Honors (LAH)": ["CLA Building"],
    "Plan II Honors": ["Parlin Hall (PAR)", "Mezes Hall (MEZ)"],
    "Business Honors Program (BHP)": ["McCombs School of Business (CBA)"],
}


# UT building coordinates
building_list = [
    ("Gates Dell Complex (GDC)", 30.2861, -97.7366),
    ("Peter O'Donnell Jr. Building (POB)", 30.2870, -97.7362),
    ("Engineering Education and Research Center (EER)", 30.2885, -97.7381),
    ("Engineering Science Building (ENS)", 30.2882, -97.7369),
    ("Engineering Teaching Center (ETC)", 30.2876, -97.7380),
    ("Norman Hackerman Building (NHB)", 30.2865, -97.7349),
    ("Biological Laboratories (BIO)", 30.2859, -97.7357),
    ("McCombs School of Business (CBA)", 30.2855, -97.7371),
    ("Goldsmith Hall (GOL)", 30.2853, -97.7387),
    ("Battle Hall (BTL)", 30.2858, -97.7390),
    ("The Perry–Castañeda Library (PCL)", 30.2839, -97.7360),
    ("Student Activity Center (SAC)", 30.2860, -97.7393),
    ("Gregory Gymnasium (GRE)", 30.2845, -97.7364),
    ("Texas Union (UNB)", 30.2872, -97.7414),
    ("Waggener Hall (WAG)", 30.2865, -97.7380),
    ("Painter Hall (PAI)", 30.2881, -97.7360),
    ("Robert Lee Moore Hall (RLM)", 30.2891, -97.7362),
    ("Welch Hall (WEL)", 30.2859, -97.7352),
    ("Parlin Hall (PAR)", 30.2858, -97.7382),
    ("Benedict Hall (BEN)", 30.2857, -97.7378),
    ("Mezes Hall (MEZ)", 30.2857, -97.7376),
    ("Sanchez Building (SZB)", 30.2842, -97.7354),
    ("College of Liberal Arts Building (CLA)", 30.2868, -97.7390),
    ("Moody College of Communication (CMA)", 30.2897, -97.7373),
    ("Jackson Geological Sciences Building (JGB)", 30.2867, -97.7347),
    ("Burdine Hall (BUR)", 30.2857, -97.7381),
    ("Homer Rainey Hall (HRH)", 30.2849, -97.7378),
    ("Winship Drama Building (WIN)", 30.2847, -97.7384),
    ("Bass Concert Hall (BCH)", 30.2890, -97.7307),
    ("Darryl K Royal Stadium (DKR)", 30.2835, -97.7322),
    ("Texas Memorial Museum (TMM)", 30.2893, -97.7305),
    ("LBJ Library (LBJ)", 30.2852, -97.7297),
    ("School of Nursing (NUR)", 30.2803, -97.7326),
    ("Dell Medical School (DMS)", 30.2769, -97.7331),
    ("University Teaching Center (UTC)", 30.2865, -97.7388),
    ("Anna Hiss Gymnasium (AHG)", 30.2888, -97.7327),
    ("Fine Arts Building (ART)", 30.2884, -97.7378),
]


# load your scraped apartment/housing data

# geocode apartment addresses
# api_key = '3136c8f8b3434617ab307882320fbc8a'
# geocoder = OpenCageGeocode(api_key)

# Function to geocode an address using OpenCage API
r'''def geocode_address(address):
    try:
        address = cleaned_address = re.sub(r'\s*,\s*[A-Za-z0-9]+$', '', address)
        result = geocoder.geocode(address)
        if result:
            lat = result[0]['geometry']['lat']
            lon = result[0]['geometry']['lng']
            return lat, lon
        else:
            print(f"Address not found: {address}")
            return None, None
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return None, None'''

# Load your CSV (replace 'your_housing_data.csv' with your actual CSV file path)
#housing_df = pd.read_csv('FinalCleanedData.csv')

# Geocode each address and add lat/lon to the dataframe
#housing_df[['latitude', 'longitude']] = housing_df['address'].apply(lambda x: pd.Series(geocode_address(x)))

# Save the result with lat/lon to a new CSV
#housing_df.to_csv('housing_with_coordinates_opencage.csv', index=False)


# define distance function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance  # Returns distance in kilometers

# find apartments close to buildings for a major

def get_apartments_near_major_avg_distance(housing_df, major, max_distance_km):
    # Get buildings for the major
    if major not in majors_to_buildings:
        print(f"Major '{major}' not found.")
        return pd.DataFrame()
    
    major_buildings = majors_to_buildings[major]
    
    # Get coordinates of those buildings
    building_coords = [(lat, lon) for name, lat, lon in building_list if name in major_buildings]
    
    if not building_coords:
        print(f"No coordinates found for buildings related to major '{major}'")
        return pd.DataFrame()

    # List to collect results
    qualifying_apartments = []

    for _, row in housing_df.iterrows():
        apt_lat = row['latitude']
        apt_lon = row['longitude']

        if pd.isna(apt_lat) or pd.isna(apt_lon):
            continue

        # Calculate distances to each major-related building
        distances = [haversine(apt_lat, apt_lon, b_lat, b_lon) for b_lat, b_lon in building_coords]
        avg_distance = sum(distances) / len(distances)

        # Filter based on average distance
        if avg_distance <= max_distance_km:
            row_copy = row.copy()
            row_copy['average_distance_km'] = avg_distance
            qualifying_apartments.append(row_copy)

    return pd.DataFrame(qualifying_apartments)


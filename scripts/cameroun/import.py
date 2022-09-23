"""
Importer des stations météorologiques Cameroun
"""

import os
from string import capwords
import pandas as pd
from stations import find_duplicate, generate_uid, create, update

# Path of the CSV file
CSV_FILE = (
    os.path.expanduser("~")
    + os.sep
    + "Meteostat"
    + os.sep
    + "weather-stations"
    + os.sep
    + "scripts"
    + os.sep
    + "cameroun"
    + os.sep
    + "stations.csv"
)

# Min. l'année dernière pour empêcher l'importation de stations inactives
MIN_LAST_YEAR = 2015


def province_code(name: str) -> str:
    """
    Convertir le nom de la region en code
    """

    if name == "ADAMAOUA":
        return "AD"
    elif name == "CENTRE":
        return "CE"
    elif name == "EST":
        return "ES"
    elif name == "EXTREME-NORD":
        return "EN"
    elif name == "LITTORAL":
        return "LT"
    elif name == "NORD":
        return "NO"
    elif name == "NORD-OUEST":
        return "NW"
    elif name == "OUEST":
        return "OU"
    elif name == "SUD":
        return "SU"
    elif name == "SURD-OUEST":
        return "SW"
    else:
        return None


# Lire l'inventaire des stations Cameroun
inventory = pd.read_csv(
    CSV_FILE,
    usecols=[0, 1, 3, 4, 6, 7, 10, 12],
    header=0,
    names=[
        "name",
        "province",
        "id",
        "wmo",
        "latitude",
        "longitude",
        "elevation",
        "last_year",
    ],
    dtype={"wmo": "string"},
)

# Process all stations
for index, row in inventory.iterrows():

    if not pd.isna(row["last_year"]) and int(row["last_year"]) >= MIN_LAST_YEAR:

        # Collect meta data
        data = {
            "name": {"en": capwords(row["name"])},
            "country": "CM",
            "region": province_code(str(row["province"])),
            "identifiers": {
                "national": str(row["id"]),
                "wmo": None if pd.isna(row["wmo"]) else str(row["wmo"]),
            },
            "location": {
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "elevation": None
                if pd.isna(row["elevation"])
                else int(round(row["elevation"])),
            },
        }

        # Obtenir une station en double potentielle
        duplicate = find_duplicate(data)

        # Vérifiez si un doublon a été trouvé
        if isinstance(duplicate, dict):
            if "distance" in duplicate and duplicate["distance"] > 100:
                continue
            data["id"] = duplicate["id"]
            update(data)
        else:
            data["id"] = generate_uid()
            create(data)

    print(row["id"])

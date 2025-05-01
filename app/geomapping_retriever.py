"""Light-weight retrieval layer that wraps geomapping.py for the chatbot."""
import pandas as pd
from pathlib import Path
from geomapping import (
    majors_to_buildings,
    get_apartments_near_major_avg_distance
)

_DATA_PATH = Path(__file__).with_suffix('').parent / "data/housing_with_coordinates_opencage.csv"
_HOUSING_DF = pd.read_csv(_DATA_PATH)

def find_apartments(major: str,
                    budget: int,
                    km_radius: float = 1.0,
                    max_results: int = 3,
                    budget_slack: float = 0.10):
    """
    Return ≤ `max_results` apartments near buildings linked to `major`,
    sorted by price then distance. Falls back to a wider radius or up to
    `budget_slack` × budget if nothing is found.
    """
    rad = km_radius
    for _ in range(3):          # try 1 km, 1.5 km, 2 km
        df = get_apartments_near_major_avg_distance(
            _HOUSING_DF, major, max_distance_km=rad
        )
        if not df.empty:
            break
        rad += 0.5

    if df.empty:                           # no spatial hits at all
        return df.head(0)

    # parse rent into an int
    df["numeric_rent"] = (
        df["price"]
        .str.extract(r"(\d[\d,]*)")[0]
        .str.replace(',', '', regex=False)
        .astype(int)
    )

    within = df[df["numeric_rent"] <= budget]
    if within.empty:                       # allow slight over-budget
        within = df[df["numeric_rent"] <= budget * (1 + budget_slack)]

    return (
        within
        .sort_values(["numeric_rent", "average_distance_km"])
        .head(max_results)
        .reset_index(drop=True)
    )

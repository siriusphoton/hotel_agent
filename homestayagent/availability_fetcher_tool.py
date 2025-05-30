import sqlite3
from prettytable import PrettyTable
from typing import Union, Dict, Any
import os
def availability_fetcher(num_people: int, 
                     check_in_datetime: str, 
                     check_out_datetime: str
                    ) -> Dict[str, Any]:
    """
    Query the hotel database for rooms matching the requested capacity and date range,
    format the results into return structured JSON
    for programmatic consumption by an ADK agent tool.

    **Args**
    num_people : int
        The minimum number of guests the room must accommodate.
    check_in_datetime : str
        The desired check-in timestamp in ISO 8601 format (e.g., "2025-05-10 14:00").
    check_out_datetime : str
        The desired check-out timestamp in ISO 8601 format (e.g., "2025-05-12 11:00").

    **Returns**
    dict
        A dictionary with two top-level keys:
        
        - "given_input_specifications": a dict echoing back the inputs plus the total count
          of matching rooms:
            - "num_people": int
            - "check_in": str
            - "check_out": str
            - "result_count": int

        - "available_rooms": either
            - A list of dicts, each representing one available room with keys:
                * "Room ID"           : int
                * "Room No"           : str
                * "Type"              : str
                * "Max Guests"        : int
                * "Price/Night"       : str (formatted with currency symbol)
                * "Building"          : str
                * "Extra Bed"         : "Yes" or "No"
                * "Extra Bed Price"   : str (formatted with currency symbol)
            - The string "No rooms available for this specification" if zero matches.


Example outputs:

    {
        "given_input_specifications": {
            "num_people": 2,
            "check_in": "2025-05-10 14:00:00",
            "check_out": "2025-05-12 11:00:00",
            "result_count": 3
        },
        "available_rooms": [
            {"Room ID": 101, "Room No": "A-101", "Type": "Deluxe", ... },
            ...
        ]
    }
    {
        "given_input_specifications": {
            "num_people": 10,
            "check_in": "2025-12-24 14:00:00",
            "check_out": "2025-12-25 11:00:00",
            "result_count": 0
        },
        "available_rooms": "No rooms available for this specification"
    }
    """
    # Establish database connection
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(SCRIPT_DIR, 'hotel.db')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build and execute availability query
    availability_query = """
    SELECT
        r.room_id AS "Room ID",
        r.room_number AS "Room No",
        rt.name AS "Type",
        rt.capacity AS "Max Guests",
        printf("₹%.2f", rt.price) AS "Price/Night",
        b.name AS "Building",
        CASE WHEN rt.extra_bed_included THEN 'Yes' ELSE 'No' END AS "Extra Bed",
        printf("₹%.2f", rt.extra_bed_price) AS "Extra Bed Price"
    FROM room r
    JOIN room_type rt ON r.room_type_id = rt.room_type_id
    JOIN building b ON rt.building_id = b.building_id
    WHERE rt.capacity >= ?
      AND r.is_active = 1
      AND r.room_id NOT IN (
          SELECT room_id
          FROM booking
          WHERE check_in_datetime < ?
            AND check_out_datetime > ?
      )
    ORDER BY rt.price ASC, rt.capacity DESC
    """

    cursor.execute(
        availability_query,
        (num_people, check_out_datetime, check_in_datetime)
    )
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    # Prepare JSON response structure
    json_data: Dict[str, Any] = {
        "given_input_specifications": {
            "num_people": num_people,
            "check_in": check_in_datetime,
            "check_out": check_out_datetime,
            "result_count": len(results)
        },
        "available_rooms": []
    }

    # If no rooms found, set message; otherwise populate list and print table
    if not results:
        json_data["available_rooms"] = "No rooms available for this specification"
    else:
        # Build and display PrettyTable
        table = PrettyTable()
        table.field_names = columns
        table.align = "l"
        for row in results:
            table.add_row(row)
        # Convert rows to list of dicts
        json_data["available_rooms"] = [
            dict(zip(columns, row))
            for row in results
        ]

    return json_data
print(availability_fetcher(2, "2025-05-10 14:00:00", "2025-05-12 11:00:00"))
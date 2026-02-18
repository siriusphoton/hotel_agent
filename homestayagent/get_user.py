import sqlite3
import os
def add_or_get_guest(name: str, phone: str, city: str) -> dict:
    """
    Adds a new guest to the database or updates an existing guest's details
    based on the unique phone number.

    Checks if a guest with the provided phone number exists. If not, inserts
    a new guest record. If yes, updates the name and city of the existing
    record associated with that phone number. The 'created_at' timestamp is
    only set on initial creation and is not updated.

    Args:
        name (str): The full name of the guest.
        phone (str): The unique phone number of the guest. Used as the key
                     for checking existence and updating.
        city (str): The city where the guest resides.

    Returns:
        dict: A dictionary containing the operation result:
              On success:
              {
                  "new_user": int,  # 1 if a new guest was created, 0 if updated
                  "guest_details": {
                      "guest_id": int,
                      "name": str,
                      "phone": str,
                      "city": str,
                      "created_at": str  # ISO format timestamp
                  }
              }
              On failure (e.g., database error, invalid input):
              {
                  "error": str  # Description of the error
              }
    """
    if not all([name.strip(), phone.strip(), city.strip()]):
        return {"error": "All fields must contain non-whitespace characters"}
    
    conn = None
    try:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(SCRIPT_DIR, 'hotel.db')
        conn = sqlite3.connect(DB_PATH)
        conn.execute("BEGIN IMMEDIATE")  # Critical for atomic operations
        cursor = conn.cursor()

        # Atomic upsert using SQLite's conflict resolution
        cursor.execute("""
            INSERT INTO guest (name, phone, city)
            VALUES (?, ?, ?)
            ON CONFLICT(phone) DO UPDATE SET
                name = excluded.name,
                city = excluded.city
            RETURNING guest_id, created_at
        """, (name, phone, city))
        
        result = cursor.fetchone()
        new_user_flag = 0 if cursor.rowcount == -1 else 1
        
        # For SQLite versions without RETURNING (compatibility layer)
        if not result:
            cursor.execute(
                "SELECT guest_id, created_at FROM guest WHERE phone = ?", 
                (phone,)
            )
            result = cursor.fetchone()
            new_user_flag = 0

        guest_id, created_at = result
        conn.commit()

        return {
            "new_user": new_user_flag,
            "guest_details": {
                "guest_id": guest_id,
                "name": name,
                "phone": phone,
                "city": city,
                "created_at": created_at
            }
        }

    except sqlite3.IntegrityError as e:
        conn.rollback()
        return {"error": f"Duplicate phone exists: {phone}"}
    except Exception as e:
        if conn: conn.rollback()
        return {"error": f"Database operation failed: {str(e)}"}
    finally:
        if conn: conn.close()
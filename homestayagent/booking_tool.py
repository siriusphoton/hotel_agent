import sqlite3
import hashlib
from datetime import datetime
import os
def booking(guest_id: int, room_id: int, num_persons: int,
                 check_in_datetime: str, check_out_datetime: str, days_charged: int,
                 extra_beds: int, extra_bed_price: float, subtotal_amount: float,
                 taxes_and_fees: float, total_price: float, advance_due_amount: float):
    """Creates a booking record in the database and generates a reference code.

    This function connects to the 'hotel.db' SQLite database, inserts a new
    booking record with the provided details, and sets the initial status
    to 'REQUESTED'. It retrieves the building ID associated with the room
    and calculates a human-readable booking reference code based on building,
    check-in date, room ID, and a hash of booking details. The database
    transaction is committed upon success or rolled back on error.

    Args:
        guest_id (int): The unique identifier for the guest making the booking.
        room_id (int): The unique identifier for the room being booked.
        num_persons (int): The number of people included in the booking.
        check_in_datetime (str): The check-in date and time in ISO format
            (e.g., 'YYYY-MM-DD HH:MM').
        check_out_datetime (str): The check-out date and time in ISO format
            (e.g., 'YYYY-MM-DD HH:MM').
        days_charged (int): The number of days the guest will be charged for.
        extra_beds (int): The number of extra beds requested.
        extra_bed_price (float): The price per extra bed.
        subtotal_amount (float): The base price for the room stay before taxes.
        taxes_and_fees (float): The amount added for taxes and other fees.
        total_price (float): The final price including subtotal, extras, and taxes.
        advance_due_amount (float): The amount required as an advance payment.

    Returns:
        dict: A dictionary containing the booking result.
              On success:
              {
                  'system_booking_id': int,  # Auto-generated DB primary key
                  'reference_code': str,     # Human-readable code (e.g., BKG-1010305-ABCDEF-12)
                  'message': str,            # Confirmation message with reference code
                  'details': {               # Dictionary mirroring input financial/stay details
                      'num_persons': int,
                      'check_in_datetime': str,
                      'check_out_datetime': str,
                      'days_charged': int,
                      'extra_beds': int,
                      'extra_bed_price': float,
                      'subtotal_amount': float,
                      'taxes_and_fees': float,
                      'total_price': float,
                      'advance_due_amount': float
                  }
              }
              On failure (e.g., invalid room_id, database error):
              {
                  'error': str  # Description of the error encountered
              }

    Side Effects:
        - Connects to and potentially modifies the 'hotel.db' SQLite database.
        - Inserts a new row into the 'booking' table.
        - Reads from the 'room' and 'booking_status' tables.
    """
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(SCRIPT_DIR, 'hotel.db')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Insert main booking data
        cursor.execute('SELECT building_id FROM room WHERE room_id = ?', (room_id,))
        room_data = cursor.fetchone()
        if not room_data:
            conn.close() # Close connection before returning error
            return {'error': f"Invalid room_id: {room_id} not found."}
        building_id = room_data[0]

        # Ensure datetime strings are valid ISO format before inserting
        try:
            check_in_dt_obj = datetime.fromisoformat(check_in_datetime)
            # check_out_dt_obj = datetime.fromisoformat(check_out_datetime) # Optional: validate checkout too
        except ValueError:
            conn.close()
            return {'error': "Invalid datetime format. Please use ISO format (YYYY-MM-DD HH:MM:SS)."}

        cursor.execute('''
            INSERT INTO booking (
                guest_id, building_id, room_id, num_persons,
                check_in_datetime, check_out_datetime,
                days_charged, extra_beds, extra_bed_price,
                subtotal_amount, taxes_and_fees, total_price,
                advance_due_amount, status_id
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                (SELECT booking_status_id FROM booking_status WHERE code = 'REQUESTED')
            )
        ''', (
            guest_id, building_id, room_id, num_persons,
            check_in_datetime, check_out_datetime,
            days_charged, extra_beds, extra_bed_price,
            subtotal_amount, taxes_and_fees, total_price, advance_due_amount
        ))

        # Get auto-incremented ID
        db_booking_id = cursor.lastrowid

        # Generate human-friendly code (not stored in DB)
        code_seed = f"{building_id}{room_id}{check_in_datetime}{days_charged}"
        short_hash = hashlib.md5(code_seed.encode()).hexdigest()[:6].upper()
        # Use the validated datetime object for formatting
        check_in_date_str = check_in_dt_obj.strftime("%d%m")
        booking_code = f"BKG-{building_id}{check_in_date_str}-{short_hash}-{room_id}"

        conn.commit()
        return {
            'system_booking_id': db_booking_id,
            'reference_code': booking_code,
            'message': f"Booking created! Use {booking_code} for reference. Please note that this is not a confirmation code. Your booking is currently in 'REQUESTED' status and will be confirmed once processed after payment.",
            'details': {
                'num_persons': num_persons,
                'check_in_datetime': check_in_datetime,
                'check_out_datetime': check_out_datetime,
                'days_charged': days_charged,
                'extra_beds': extra_beds,
                'extra_bed_price': extra_bed_price,
                'subtotal_amount': subtotal_amount,
                'taxes_and_fees': taxes_and_fees,
                'total_price': total_price,
                'advance_due_amount': advance_due_amount
            }
        }

    except sqlite3.Error as db_err: # Catch specific DB errors
        conn.rollback()
        return {'error': f"Database error: {db_err}"}
    except Exception as e:
        conn.rollback()
        # Log the full error for debugging if needed
        # print(f"Unexpected error during booking: {e}")
        return {'error': f"An unexpected error occurred: {e}"}

    finally:
        # Ensure connection is always closed
        if conn:
            conn.close()
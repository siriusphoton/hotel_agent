from mcp.server.fastmcp import FastMCP
from homestayagent.availability_fetcher_tool import availability_fetcher
from homestayagent.booking_tool import booking
from homestayagent.get_user import add_or_get_guest
from homestayagent.prompts import coordinator_instructions
# Initialize the FastMCP server
mcp = FastMCP("HomeStayAgent")

# Expose the System Prompt
@mcp.prompt()
def homestay_system_prompt() -> str:
    """The system instructions for the Homestay Coordinator."""
    return coordinator_instructions

# Expose the Tools
@mcp.tool()
def get_guest_or_register(name: str, phone: str, city: str) -> dict:
    """
    Adds a new guest to the database or updates an existing guest's details 
    based on the unique phone number.
    """
    return add_or_get_guest(name, phone, city)

@mcp.tool()
def fetch_room_availability(num_people: int, check_in_datetime: str, check_out_datetime: str) -> dict:
    """
    Query the hotel database for rooms matching the requested capacity and date range.
    """
    return availability_fetcher(num_people, check_in_datetime, check_out_datetime)

@mcp.tool()
def create_hotel_booking(guest_id: int, room_id: int, num_persons: int,
                 check_in_datetime: str, check_out_datetime: str, days_charged: int,
                 extra_beds: int, extra_bed_price: float, subtotal_amount: float,
                 taxes_and_fees: float, total_price: float, advance_due_amount: float) -> dict:
    """
    Creates a booking record in the database and generates a reference code.
    """
    return booking(guest_id, room_id, num_persons, check_in_datetime, check_out_datetime, 
                   days_charged, extra_beds, extra_bed_price, subtotal_amount, 
                   taxes_and_fees, total_price, advance_due_amount)

if __name__ == "__main__":
    # Run the server using standard input/output (required for MCP)
    mcp.run(transport="sse")







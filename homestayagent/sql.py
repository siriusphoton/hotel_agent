import sqlite3
from prettytable import PrettyTable

conn=sqlite3.connect("hotel.db")
cursor=conn.cursor()
while(1):
	inp=input()
	cursor.execute(inp)
	conn.commit()
	results = cursor.fetchall()
	table = PrettyTable()
	if results:
		table.field_names = [desc[0] for desc in cursor.description]
	table.align = "l"
	for row in results:
		table.add_row(row)
	print(f"Available Rooms ({len(results)} options):\n{table}")

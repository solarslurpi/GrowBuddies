
table_name = input("Enter the table name where SnifferBuddyReadings will be Stored (Default is SnifferBuddyReadings): ")
if not table_name or table_name == "":
    table_name = "SnifferBuddyReadings"
print(f"The table name is >>>{table_name}<<<")
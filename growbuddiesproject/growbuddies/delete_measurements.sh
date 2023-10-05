#!/bin/bash

# Set the database name
DB_NAME="gus"

# Get all measurements
MEASUREMENTS=$(influx -database $DB_NAME -execute 'SHOW MEASUREMENTS' -format csv | tail -n +2 | awk -F ',' '{print $2}')

# Drop each measurement
for measurement in $MEASUREMENTS; do
  influx -database $DB_NAME -execute "DROP MEASUREMENT \"$measurement\""
  echo "Dropped measurement: $measurement"
done

echo "All measurements in $DB_NAME have been deleted."

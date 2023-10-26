from(bucket: "snifferbuddy")
|> range(start: -1h)
|> filter(fn: (r) => r["_measurement"] == "snifferbuddy" and r._field == "temperature")


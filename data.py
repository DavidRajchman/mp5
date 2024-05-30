import sqlite3
import random
import datetime

# Connect to SQLite database
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS temperatures
             (timestamp TEXT, temperature REAL)''')

# Generate 100 temperature recordings
for i in range(100):
    # Generate a random temperature between 15 and 30
    temperature = random.uniform(15, 30)
    # Round the temperature to 2 digits
    temperature = round(temperature, 2)
    
    # Generate a timestamp 5 minutes apart
    timestamp = (datetime.datetime.now() + datetime.timedelta(minutes=i*5)).strftime("%H:%M")
    
    # Insert the recording into the database
    c.execute("INSERT INTO temperatures VALUES (?, ?)", (timestamp, temperature))

# Save (commit) the changes
conn.commit()

# Close the connection
conn.close()
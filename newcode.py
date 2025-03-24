import pandas as pd
import re

# Define file names
input_file = "123.txt"
output_file = "aerospike_log.xlsx"

# List to store extracted records
data = []

# Regular expression to match "Set Name" and "Key"
set_key_pattern = re.compile(r"Set Name:\s*(.*?),\s*Key:\s*(.*?),\s*JSON Data:\s*{")

# Open and read the file line by line
with open(input_file, "r", encoding="utf-8") as file:
    current_set = None
    current_key = None
    inside_json = False  # Flag to track JSON Data section

    for line in file:
        line = line.strip()

        # Detect a new log entry (Set Name & Key)
        match = set_key_pattern.match(line)
        if match:
            current_set = match.group(1).strip()
            current_key = match.group(2).strip()
            inside_json = True  # Start processing JSON fields
            continue  # Move to the next line

        # If inside JSON section, extract key-value pairs
        if inside_json:
            # Remove trailing commas or extra spaces
            line = line.rstrip(", ")

            # If it's the end of JSON block, stop processing
            if line == "}":
                inside_json = False
                continue

            # Extract field and value
            if ":" in line:
                parts = line.split(":", 1)
                field = parts[0].strip().replace('"', '')
                value = parts[1].strip()

                # Handle multi-line lists (like documentNames)
                if value.startswith("["):
                    value_list = []
                    while not value.endswith("]"):
                        try:
                            line = next(file).strip().rstrip(", ")
                            value_list.append(line.strip().replace('"', ''))
                            value = line.strip()  # Update last read value
                        except StopIteration:
                            break  # Avoid crash if file ends unexpectedly

                    value = "[" + ", ".join(value_list) + "]"  # Reconstruct list format

                # Store extracted data
                data.append([current_set, current_key, field, value])

# Create DataFrame
df = pd.DataFrame(data, columns=["Set Name", "Key", "Field", "Value"])

# Save to Excel
df.to_excel(output_file, index=False)

print(f"✅ Excel file '{output_file}' has been created successfully.")

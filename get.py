import json

file_path = 'profiles.json'
output_file_path = 'accounts.txt'

# Read data from the json file
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract email and password and write to accounts.txt
with open(output_file_path, 'w') as output_file:
    for username, user_data in data.items():
        email = user_data['email']
        password = user_data['password']

        # Print email and password
        print(f"{email}|{password}")

        # Write to accounts.txt
        output_file.write(f"{email}|{password}\n")

# Clear the data in the json file
with open(file_path, 'w') as file:
    file.write('{}')

print("Data written to accounts.txt and cleared from the file.")

import os

if not os.path.isfile(".env"):
    print("No .env file found. Please run this script in the same directory as the .env file.")
    exit()

token = input("Enter your token: ")

f = open(".env", "r") # Open .env file
lines = f.readlines()
f.close()

f = open(".env", "w")
for line in lines: # Write new token
    if line.startswith("VNC_AUTH="):
        print("Token updated")
        f.write(f"VNC_AUTH={token}\n")
    else:
        f.write(line)
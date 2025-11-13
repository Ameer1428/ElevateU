import os
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['elevateu']
users_collection = db['users']

# Find all students with name containing 'Ameer'
students = list(users_collection.find({'name': {'$regex': 'Ameer', '$options': 'i'}}))
print(f'Found {len(students)} students with name containing Ameer:')
for student in students:
    print(f'ID: {student["_id"]}, Name: {student["name"]}, Email: {student.get("email", "N/A")}, ClerkID: {student.get("clerkId", "N/A")}')

# Check for duplicate clerk IDs or emails
print('\nChecking for duplicates...')
all_students = list(users_collection.find({'role': 'student'}))
clerk_ids = {}
emails = {}
for student in all_students:
    clerk_id = student.get('clerkId')
    email = student.get('email')
    if clerk_id:
        if clerk_id in clerk_ids:
            print(f'Duplicate clerkId found: {clerk_id} - Students: {clerk_ids[clerk_id]["name"]} and {student["name"]}')
        else:
            clerk_ids[clerk_id] = student
    if email:
        if email in emails:
            print(f'Duplicate email found: {email} - Students: {emails[email]["name"]} and {student["name"]}')
        else:
            emails[email] = student

print(f'\nTotal students in database: {len(all_students)}')
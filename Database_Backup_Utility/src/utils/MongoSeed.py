from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
connection_string = "mongodb+srv://asim4ch:V5fX3qYv25GuGeKh@cluster.13hzz.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)
db = client['sample_inventory']

try:
    # The ping command is lightweight and checks connectivity
    client.admin.command('ping')
    print("Connected successfully to MongoDB Atlas!")
except Exception as e:
    print(f"Connection failed: {e}")

# Insert collection data
products = [

{
    "_id": 1,
    "name": "Laptop Pro X",
    "category": "Electronics",
    "price": 1299.99,
    "stock": 45,
    "specs": {
        "processor": "Intel i7",
        "memory": "16GB",
        "storage": "512GB SSD"
    },
    "tags": ["laptop", "high-end", "business"]
},

    {
    "_id": 2,
    "name": "Digital Camera Pro",
    "category": "Photography",
    "price": 849.99,
    "stock": 32,
    "specs": {
        "megapixels": "24MP",
        "zoom": "30x optical",
        "stabilization": "5-axis"
    },
    "tags": ["camera", "professional", "photography"]
},

{
    "_id": 3,
    "name": "Gaming Console X",
    "category": "Gaming",
    "price": 499.99,
    "stock": 15,
    "specs": {
        "processor": "Custom AMD",
        "memory": "16GB GDDR6",
        "storage": "1TB SSD"
    },
    "tags": ["gaming", "entertainment", "console"]
},

{
    "_id": 4,
    "name": "Smart Speaker",
    "category": "Smart Home",
    "price": 89.99,
    "stock": 150,
    "specs": {
        "connectivity": "WiFi/Bluetooth",
        "assistant": "Voice AI",
        "audioOutput": "360° sound"
    },
    "tags": ["smart home", "audio", "assistant"]
}

]

users = [

    {
        "_id": 1,
        "username": "tech_enthusiast",
        "email": "tech@example.com",
        "profile": {
            "name": "Alex Johnson",
            "age": 32,
            "location": "San Francisco, CA"
        },
        "preferences": {
            "notifications": True,
            "theme": "dark",
            "language": "en-US"
        },
        "purchase_history": [2, 3],
        "account_type": "premium",
        "joined_date": "2024-01-15"
    },
    {
        "_id": 2,
        "username": "photo_pro",
        "email": "photo@example.com",
        "profile": {
            "name": "Sam Williams",
            "age": 29,
            "location": "New York, NY"
        },
        "preferences": {
            "notifications": False,
            "theme": "light",
            "language": "en-US"
        },
        "purchase_history": [2],
        "account_type": "professional",
        "joined_date": "2023-11-05"
    },
    {
        "_id": 3,
        "username": "game_master",
        "email": "gamer@example.com",
        "profile": {
            "name": "Jordan Smith",
            "age": 25,
            "location": "Austin, TX"
        },
        "preferences": {
            "notifications": True,
            "theme": "dark",
            "language": "en-US"
        },
        "purchase_history": [3, 4],
        "account_type": "standard",
        "joined_date": "2024-02-20"
    },
    {
        "_id": 4,
        "username": "smart_home_lover",
        "email": "smart@example.com",
        "profile": {
            "name": "Taylor Reed",
            "age": 34,
            "location": "Seattle, WA"
        },
        "preferences": {
            "notifications": True,
            "theme": "auto",
            "language": "en-GB"
        },
        "purchase_history": [4],
        "account_type": "premium",
        "joined_date": "2023-08-12"
    }
]

movies = [
    {
        "_id": 1,
        "title": "The Digital Frontier",
        "release_year": 2023,
        "genre": ["Sci-Fi", "Adventure"],
        "runtime": 142,
        "ratings": {
            "critics": 8.7,
            "audience": 9.2,
            "certified": True
        },
        "production": {
            "studio": "Future Films",
            "budget": 185000000,
            "director": "Emma Rodriguez"
        },
        "cast": ["Michael Chen", "Sophia Patel", "David Kim"],
        "available_on_streaming": True
    },
    {
        "_id": 2,
        "title": "Echoes of Tomorrow",
        "release_year": 2024,
        "genre": ["Drama", "Mystery"],
        "runtime": 128,
        "ratings": {
            "critics": 9.1,
            "audience": 8.5,
            "certified": True
        },
        "production": {
            "studio": "Visionary Pictures",
            "budget": 65000000,
            "director": "James Wilson"
        },
        "cast": ["Olivia Martinez", "Benjamin Thomas", "Zoe Johnson"],
        "available_on_streaming": False
    },
    {
        "_id": 3,
        "title": "The Last Algorithm",
        "release_year": 2022,
        "genre": ["Thriller", "Sci-Fi"],
        "runtime": 135,
        "ratings": {
            "critics": 7.8,
            "audience": 8.9,
            "certified": True
        },
        "production": {
            "studio": "Quantum Studios",
            "budget": 120000000,
            "director": "Noah Garcia"
        },
        "cast": ["Ethan Williams", "Ava Thompson", "Lucas Brown"],
        "available_on_streaming": True
    },
    {
        "_id": 4,
        "title": "Whispers in the Code",
        "release_year": 2023,
        "genre": ["Horror", "Tech-Thriller"],
        "runtime": 115,
        "ratings": {
            "critics": 8.2,
            "audience": 7.6,
            "certified": False
        },
        "production": {
            "studio": "Midnight Films",
            "budget": 45000000,
            "director": "Isabella Chen"
        },
        "cast": ["Jackson Moore", "Lily Zhang", "Ryan Cooper", "Maya Patel"],
        "available_on_streaming": True
    }
]


db.users.insert_many(users)
db.movies.insert_many(movies)
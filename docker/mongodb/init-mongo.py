#!/usr/bin/env python3

import json
import os
from pymongo import MongoClient
import time

def initialize_database():
    # Wait for MongoDB to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            # Connect to MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            
            # Test connection
            client.admin.command('ping')
            print("MongoDB connection successful!")
            break
        except Exception as e:
            print(f"Waiting for MongoDB... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("Failed to connect to MongoDB after maximum retries")
        return False

    try:
        # Initialize the Pokemon database
        db = client['pokemon_db']
        
        # Create the pokemons collection
        collection = db['pokemons']
        
        # Load sample data
        with open('/docker-entrypoint-initdb.d/sample-data.json', 'r') as f:
            pokemon_data = json.load(f)
        
        # Clear existing data (if any)
        collection.drop()
        
        # Insert sample data
        result = collection.insert_many(pokemon_data)
        print(f"Inserted {len(result.inserted_ids)} Pokemon records")
        
        # Create indexes for better performance
        collection.create_index("id", unique=True)
        collection.create_index("name", unique=True)
        print("Created indexes on id and name fields")
        
        # Verify data insertion
        count = collection.count_documents({})
        print(f"Total Pokemon in database: {count}")
        
        # Show sample data
        sample = collection.find_one()
        print(f"Sample Pokemon: {sample}")
        
        print("Pokemon database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    initialize_database()
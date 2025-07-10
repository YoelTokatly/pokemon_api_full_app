#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient
import sys

def test_mongodb_connection():
    """Test MongoDB connection with different methods"""
    
    # Method 1: Simple connection (no auth)
    print("Testing Method 1: Simple connection...")
    try:
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ Method 1: Connected successfully (no auth)")
        client.close()
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: With authentication
    print("\nTesting Method 2: With authentication...")
    try:
        client = MongoClient(
            'mongodb://admin:pokemon123@localhost:27017/pokemon_db?authSource=admin',
            serverSelectionTimeoutMS=2000
        )
        client.admin.command('ping')
        print("✅ Method 2: Connected successfully (with auth)")
        
        # Test database access
        db = client.pokemon_db
        collection = db.pokemons
        count = collection.count_documents({})
        print(f"✅ Found {count} Pokemon in database")
        
        client.close()
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Check if MongoDB is running
    print("\nTesting Method 3: Basic port check...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 27017))
        sock.close()
        if result == 0:
            print("✅ Port 27017 is open")
        else:
            print("❌ Port 27017 is closed or unreachable")
    except Exception as e:
        print(f"❌ Port check failed: {e}")

if __name__ == "__main__":
    test_mongodb_connection()
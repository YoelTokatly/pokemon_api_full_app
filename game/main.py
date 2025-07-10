import requests
import random as rd
import json
import os
from datetime import datetime

class pokemon_game:
    # Configuration
    FLASK_API_BASE_URL = os.getenv('FLASK_API_URL', 'http://localhost:5000')
    POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"

    @staticmethod
    def main():
        """Main game loop"""
        print("=" * 50)
        print("🎮 Welcome to the Pokemon Game! 🎮")
        print("=" * 50)
        
        while True:
            print("\nChoose an option:")
            print("1. Draw a random Pokemon")
            print("2. View all collected Pokemon")
            print("3. Search for a Pokemon by name")
            print("4. Get Pokemon by ID")
            print("5. Delete a Pokemon")
            print("6. View game statistics")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                pokemon_game.draw_a_card()
            elif choice == '2':
                pokemon_game.view_all_pokemon()
            elif choice == '3':
                pokemon_game.search_pokemon_by_name()
            elif choice == '4':
                pokemon_game.get_pokemon_by_id()
            elif choice == '5':
                pokemon_game.delete_pokemon()
            elif choice == '6':
                pokemon_game.view_statistics()
            elif choice == '7':
                print("Thanks for playing! Goodbye! 👋")
                break
            else:
                print("❌ Invalid choice. Please try again.")

    @staticmethod
    def draw_a_card():
        """Draw a random Pokemon from PokeAPI and save to our database"""
        try:
            print("\n🎲 Drawing a random Pokemon...")
            
            # Get list of Pokemon from PokeAPI
            endpoint = "pokemon/"
            pokeapi_data = pokemon_game.api_get(pokemon_game.POKEAPI_BASE_URL, endpoint)
            
            if not pokeapi_data:
                print("❌ Failed to fetch Pokemon list from PokeAPI")
                return
            
            # Select a random Pokemon from the list (without pandas)
            pokemon_list = pokeapi_data['results']
            random_pokemon = rd.choice(pokemon_list)
            
            print(f"🔍 Selected: {random_pokemon['name'].title()}")
            
            # Check if Pokemon already exists in our database
            exists_response = pokemon_game.check_pokemon_exists(random_pokemon['name'])
            
            if exists_response and exists_response.get('exists'):
                print(f"📦 {random_pokemon['name'].title()} is already in your collection!")
                
                # Show existing Pokemon details
                pokemon_response = pokemon_game.get_pokemon_from_api(random_pokemon['name'])
                if pokemon_response and pokemon_response.get('success'):
                    pokemon_game.display_pokemon(pokemon_response['data'])
                return
            
            # Fetch detailed Pokemon data from PokeAPI
            print("📡 Fetching Pokemon details...")
            pokemon_data = pokemon_game.api_get(random_pokemon['url'], "")
            
            if not pokemon_data:
                print("❌ Failed to fetch Pokemon details")
                return
            
            # Save to our database
            save_response = pokemon_game.save_to_api({
                'id': pokemon_data['id'],
                'name': pokemon_data['name'],
                'height': pokemon_data['height'],
                'weight': pokemon_data['weight'],
                'base_experience': pokemon_data.get('base_experience', 0),
                'pokemon_order': pokemon_data.get('order', 0)
            })
            
            if save_response and save_response.get('success'):
                print(f"✅ {pokemon_data['name'].title()} has been added to your collection!")
                pokemon_game.display_pokemon(save_response['data'])
            else:
                print(f"❌ Failed to save Pokemon: {save_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error drawing Pokemon: {e}")

    @staticmethod
    def view_all_pokemon():
        """View all Pokemon in the collection"""
        try:
            print("\n📋 Your Pokemon Collection:")
            
            response = requests.get(f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    pokemons = data['data']
                    print(f"\n🎯 Total Pokemon: {data.get('total', len(pokemons))}")
                    print("-" * 80)
                    
                    # Display Pokemon in a nice table format (without pandas)
                    print(f"{'ID':<4} | {'Name':<15} | {'Height':<6} | {'Weight':<6} | {'XP':<4}")
                    print("-" * 80)
                    
                    for pokemon in pokemons:
                        print(f"{pokemon.get('id', 'N/A'):<4} | "
                              f"{pokemon.get('name', 'Unknown').title():<15} | "
                              f"{pokemon.get('height', 0):<6} | "
                              f"{pokemon.get('weight', 0):<6} | "
                              f"{pokemon.get('base_experience', 0):<4}")
                    print("-" * 80)
                else:
                    print("📭 Your collection is empty! Draw some Pokemon first.")
            else:
                print(f"❌ Failed to fetch Pokemon collection: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error viewing collection: {e}")

    @staticmethod
    def search_pokemon_by_name():
        """Search for a Pokemon by name"""
        try:
            name = input("\n🔍 Enter Pokemon name: ").strip().lower()
            if not name:
                print("❌ Please enter a valid name")
                return
            
            response = pokemon_game.get_pokemon_from_api(name)
            
            if response and response.get('success'):
                print(f"\n✅ Found {name.title()}!")
                pokemon_game.display_pokemon(response['data'])
            else:
                print(f"❌ Pokemon '{name.title()}' not found in your collection")
                
        except Exception as e:
            print(f"❌ Error searching Pokemon: {e}")

    @staticmethod
    def get_pokemon_by_id():
        """Get a Pokemon by its ID"""
        try:
            pokemon_id = input("\n🔢 Enter Pokemon ID: ").strip()
            if not pokemon_id.isdigit():
                print("❌ Please enter a valid numeric ID")
                return
            
            response = requests.get(f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons/{pokemon_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"\n✅ Found Pokemon with ID {pokemon_id}!")
                    pokemon_game.display_pokemon(data['data'])
                else:
                    print(f"❌ {data.get('error', 'Pokemon not found')}")
            else:
                print(f"❌ Pokemon with ID {pokemon_id} not found")
                
        except Exception as e:
            print(f"❌ Error getting Pokemon: {e}")

    @staticmethod
    def delete_pokemon():
        """Delete a Pokemon from the collection"""
        try:
            pokemon_id = input("\n🗑️ Enter Pokemon ID to delete: ").strip()
            if not pokemon_id.isdigit():
                print("❌ Please enter a valid numeric ID")
                return
            
            # First, get the Pokemon to show what will be deleted
            get_response = requests.get(f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons/{pokemon_id}")
            
            if get_response.status_code != 200:
                print(f"❌ Pokemon with ID {pokemon_id} not found")
                return
            
            pokemon_data = get_response.json()['data']
            print(f"\n⚠️ You are about to delete: {pokemon_data['name'].title()} (ID: {pokemon_id})")
            
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Deletion cancelled")
                return
            
            # Delete the Pokemon
            response = requests.delete(f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons/{pokemon_id}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {pokemon_data['name'].title()} has been deleted from your collection")
                else:
                    print(f"❌ {data.get('error', 'Failed to delete Pokemon')}")
            else:
                print(f"❌ Failed to delete Pokemon: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error deleting Pokemon: {e}")

    @staticmethod
    def view_statistics():
        """View game statistics"""
        try:
            print("\n📊 Game Statistics:")
            
            response = requests.get(f"{pokemon_game.FLASK_API_BASE_URL}/api/stats")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data['stats']
                    print(f"🎯 Total Pokemon Collected: {stats.get('total_pokemons', 0)}")
                    print(f"💾 Database: {stats.get('database', 'N/A')}")
                    print(f"📦 Collection: {stats.get('collection', 'N/A')}")
                else:
                    print(f"❌ {data.get('error', 'Failed to get statistics')}")
            else:
                print(f"❌ Failed to fetch statistics: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")

    @staticmethod
    def display_pokemon(pokemon_data):
        """Display Pokemon details in a nice format"""
        print("\n" + "=" * 50)
        print(f"🎮 Pokemon Details")
        print("=" * 50)
        print(f"ID: {pokemon_data.get('id', 'N/A')}")
        print(f"Name: {pokemon_data.get('name', 'Unknown').title()}")
        print(f"Height: {pokemon_data.get('height', 0)} decimeters")
        print(f"Weight: {pokemon_data.get('weight', 0)} hectograms")
        print(f"Base Experience: {pokemon_data.get('base_experience', 0)}")
        print(f"Order: {pokemon_data.get('pokemon_order', 0)}")
        
        if 'created_at' in pokemon_data:
            print(f"Added to collection: {pokemon_data['created_at']}")
        
        print("=" * 50)

    @staticmethod
    def api_get(base_url, endpoint):
        """Make GET request to API"""
        try:
            url = f"{base_url}{endpoint}"
            if not endpoint:  # If endpoint is empty, base_url is the full URL
                url = base_url
                
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None

    @staticmethod
    def save_to_api(pokemon_data):
        """Save Pokemon data to our Flask API"""
        try:
            response = requests.post(
                f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons",
                json=pokemon_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"❌ Save failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error while saving: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_pokemon_from_api(name):
        """Get Pokemon from our Flask API by name"""
        try:
            response = requests.get(
                f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons/name/{name}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': 'Pokemon not found'}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def check_pokemon_exists(name):
        """Check if Pokemon exists in our database"""
        try:
            response = requests.get(
                f"{pokemon_game.FLASK_API_BASE_URL}/api/pokemons/exists/{name}",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'exists': False}
                
        except requests.exceptions.RequestException as e:
            return {'success': False, 'exists': False}


if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional
    
    # Start the game
    pokemon_game.main()
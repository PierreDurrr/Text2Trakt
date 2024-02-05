import requests
from tmdbv3api import TMDb
from tmdbv3api import TV
import time

# Initialize TMDB API
tmdb = TMDb()
tmdb.api_key = 'YOUR_TMDB_API_KEY'

tvdb = TV()

def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.readlines()

def create_trakt_list(list_file):
    base_url = "https://api.trakt.tv"
    headers = {
        "Content-Type": "application/json",
        "trakt-api-key": "YOUR_TRAKT_API_KEY",
        "trakt-api-version": "2",
        "Authorization": f"Bearer YOUR_TRAKT_TOKEN",
    }

    # Read Trakt list name and show titles from file
    lines = read_file(list_file)
    list_name = lines[0].strip().replace("List Name:", "")
    shows = [line.strip() for line in lines[2:]]  # Changed to 'shows'

    print(f"List Name: {list_name}")
    print("Shows:")

    # Check if the list already exists
    list_id = get_trakt_list_id(list_name, base_url, headers)

    if not list_id:
        # Create a new list if it doesn't exist
        list_id = create_new_trakt_list(list_name, base_url, headers)
        if not list_id:
            return

    # Add shows to the list
    for show in shows:
        # Check if the show exists on Trakt
        if not trakt_show_exists(show):
            # If not found on Trakt, try to search on TMDB
            tmdb_show = search_tmdb_show(show)
            if tmdb_show:
                # If found on TMDB, add it to Trakt
                add_tmdb_show_to_trakt(tmdb_show, base_url, headers, list_id)
            else:
                print(f"Show '{show}' not found on Trakt or TMDB.")

        # Add a delay to avoid rate limit issues
        time.sleep(1)

def get_trakt_list_id(list_name, base_url, headers):
    # Retrieve the ID of the list if it exists
    url = f"{base_url}/users/me/lists/{list_name}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["ids"]["trakt"]
    else:
        return None

def create_new_trakt_list(list_name, base_url, headers):
    # Create a new list
    create_list_url = f"{base_url}/users/me/lists"
    list_payload = {"name": list_name, "privacy": "public"}
    response_create = requests.post(create_list_url, headers=headers, json=list_payload)

    if response_create.status_code == 201:
        print(f"Created new list '{list_name}' on Trakt.")
        return response_create.json()["ids"]["trakt"]
    else:
        print(f"Failed to create list '{list_name}' on Trakt.")
        print(response_create.text)
        return None

def trakt_show_exists(show_title):
    # Implement Trakt show existence checking logic here
    pass

def search_tmdb_show(show_title):
    search_result = tvdb.search(show_title)
    if search_result:
        return search_result[0]  # Return the first search result
    else:
        return None

def add_tmdb_show_to_trakt(tmdb_show, base_url, headers, list_id):
    # Add the show to the list
    add_items_url = f"{base_url}/users/me/lists/{list_id}/items"
    items_payload = {"shows": [{"title": tmdb_show.name}]}
    response_add_items = requests.post(add_items_url, headers=headers, json=items_payload)

    if response_add_items.status_code == 201:
        print(f"Show '{tmdb_show.name}' added successfully to Trakt list '{list_id}'.")
    else:
        print(f"Failed to add show '{tmdb_show.name}' to Trakt list '{list_id}'.")
        print(response_add_items.text)

# Example usage
create_trakt_list("trakt_list.txt")

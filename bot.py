import requests
import sys
import io
from colorama import Fore, Style, init
from datetime import datetime, timedelta
import time

# Initialize colorama for colored terminal output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
init(autoreset=True)

# API URLs (adjust as necessary)
url_login = "https://atletaclicker.online/api/v1/users"  # The login or auth endpoint
url_claim = "https://atletaclicker.online/api/v1/claim"  # The claim endpoint
url_boost = "https://atletaclicker.online/api/v1/boosts"  # Boost tasks endpoint
url_social_tasks = "https://atletaclicker.online/api/v1/socials"  # Social tasks endpoint

# User-Agent for the request headers
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"

# Function to read query_id from a text file (e.g., data.txt)
def read_query_ids(file_path):
    with open(file_path, 'r') as file:
        # Return a list of query IDs, each line being a separate ID
        return [line.strip() for line in file.readlines()]

# Function to get the Bearer token and username from the login response
def get_bearer_token_and_username(query_id):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",  # Ensure correct Content-Type
        "User-Agent": user_agent
    }
    
    # The body that might be needed to authenticate
    body = {
        "query_id": query_id,  # query_id as a parameter
        "initData": query_id   # Same query_id passed as initData
    }

    try:
        # Make a POST request to the login/auth endpoint
        response = requests.post(url_login, headers=headers, json=body, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError if the status is not 200

        # Extract the Bearer token and username from the 'data' object
        response_json = response.json()
        token = response_json.get('token')
        data = response_json.get('data')
        username = data.get('username') if data else None

        # Ensure both token and username are found
        if token and username:
            print(f"Berhasil login sebagai {username}.")
            return token, username
        else:
            print(f"{Fore.RED}Token atau username tidak ditemukan dalam respons.{Style.RESET_ALL}")
            return None, None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"Request error saat mendapatkan token otorisasi: {e}")
        return None, None

# Function to get available boost tasks and their status
def get_boost_tasks(token, username):
    headers = {
        "Authorization": f"Bearer {token}",  # Use the Bearer token in the headers
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }

    try:
        # Make a GET request to the boost endpoint
        response = requests.get(url_boost, headers=headers, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError if the status is not 200
        boost_data = response.json()

        tasks = boost_data.get('data', [])
        if tasks:
            print(f"{Fore.GREEN}Boost tasks ditemukan untuk username {username}.{Style.RESET_ALL}")
            for task in tasks:
                task_id = task.get('_id')
                task_name = task.get('name')
                boost_time = task.get('boostTime')
                boost_amount = task.get('boostAmount')
                started_timestamp = task.get('startedTimestamp')
                end_timestamp = task.get('endTimestamp')

                print(f"Task ID: {task_id}, Task Name: {task_name}, Boost Time: {boost_time} hours, Boost Amount: {boost_amount}")
                
                # Handle boost task status
                if started_timestamp is None:
                    print(f"{Fore.YELLOW}Task {task_name} (ID: {task_id}) belum diaktifkan.{Style.RESET_ALL}")
                elif started_timestamp and end_timestamp is None:
                    print(f"{Fore.CYAN}Task {task_name} (ID: {task_id}) sedang berjalan.{Style.RESET_ALL}")
                elif end_timestamp:
                    print(f"{Fore.GREEN}Task {task_name} (ID: {task_id}) telah selesai.{Style.RESET_ALL}")

            return tasks
        else:
            print(f"{Fore.YELLOW}Tidak ada boost tasks yang tersedia untuk username {username}.{Style.RESET_ALL}")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during boost task retrieval for username {username}: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request error saat mendapatkan boost tasks untuk username {username}: {e}")

# Function to fetch and log social tasks
def get_social_tasks(token, username):
    headers = {
        "Authorization": f"Bearer {token}",  # Use the Bearer token in the headers
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }

    try:
        # Make a GET request to the social tasks endpoint
        response = requests.get(url_social_tasks, headers=headers, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError if the status is not 200
        social_data = response.json()

        tasks = social_data.get('data', [])
        if tasks:
            print(f"{Fore.GREEN}Social tasks ditemukan untuk username {username}.{Style.RESET_ALL}")
            for task in tasks:
                task_id = task.get('_id')
                task_name = task.get('name')
                task_status = task.get('status')

                print(f"Task ID: {task_id}, Task Name: {task_name}, Status: {task_status}")
                # Optionally, handle social task completion here

            return tasks
        else:
            print(f"{Fore.YELLOW}Tidak ada social tasks yang tersedia untuk username {username}.{Style.RESET_ALL}")
            return []

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during social task retrieval for username {username}: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request error saat mendapatkan social tasks untuk username {username}: {e}")

# Function to make a claim using the Bearer token and username
def claim_rewards(token, username):
    headers = {
        "Authorization": f"Bearer {token}",  # Use the Bearer token in the headers
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }

    # Payload for the claim request
    payload = {
        "telegramId": username  # Automatically retrieved Telegram ID (represented by username)
    }

    try:
        # Make a POST request to the claim endpoint
        response = requests.post(url_claim, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError if the status is not 200

        # Process the response data
        claim_data = response.json()

        # Check if the claim was successful
        claimed_points = claim_data.get('data', {}).get('claimedPoints')

        if claimed_points:
            print(f"{Fore.GREEN}Berhasil klaim {claimed_points:.2f} poin untuk username {username}.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Claim belum tersedia untuk username {username}.{Style.RESET_ALL}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during claim for username {username}: {http_err}")
        print(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request error saat melakukan klaim untuk username {username}: {e}")

if __name__ == "__main__":
    # Set the loop interval in seconds (e.g., every 15 minutes)
    loop_interval = 120 * 60  # 15 minutes

    # Load query_id from file
    query_ids = read_query_ids('data.txt')
    if not query_ids:
        print(f"{Fore.RED}Gagal membaca query_id dari data.txt.{Style.RESET_ALL}")
        sys.exit()

    while True:
        # Loop through each query ID in the list
        for query_id in query_ids:
            # Get the Bearer token and username from the login response
            token, username = get_bearer_token_and_username(query_id)
            if token and username:
                # Fetch available boost tasks
                get_boost_tasks(token, username)

                # Fetch available social tasks
                get_social_tasks(token, username)

                # Make the claim request
                claim_rewards(token, username)
            else:
                print(f"{Fore.RED}Gagal mendapatkan token atau username untuk query_id: {query_id}.{Style.RESET_ALL}")

        # Wait for the next loop
        print(f"{Fore.BLUE}Menunggu {loop_interval / 60} menit sebelum melakukan eksekusi berikutnya...{Style.RESET_ALL}")
        time.sleep(loop_interval)
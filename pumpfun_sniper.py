import requests
import time
import argparse
import sys
import threading

# ANSI color codes
RESET_COLOR = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"

# Define the domain of the API
domain = "frontend-api.pump.fun"

# By default the change percentage is 50%
# i.e if a coin goes up by 50%, then sell.
# You can change the value as needed
change_percentage = 50

#minimum market cap for new coins
min_market_cap = 4000

# Define the URLs using the domain for coin listing and monitoring
list_url = f"https://{domain}/coins/for-you?offset=0&limit=50&includeNsfw=false"
monitor_url = f"https://{domain}/coins/"
user_url = f"https://{domain}/users/"
order_url = f"https://{domain}/orders"
sell_order_url = f"https://{domain}/sell-order"

# Function to fetch data from the API
def fetch_coin_data():
    try:
        response = requests.get(list_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to fetch data for a specific coin by mint ID
def fetch_coin_by_mint(mint):
    try:
        response = requests.get(monitor_url + mint)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coin {mint}: {e}")
        return None

# Function to sell coins
def sell_coins(mint, amount='all', private_key=None, seed_phrase=None):
    sell_data = {
        "mint": mint,
        "amount": amount
    }
    try:
        response = requests.post(sell_order_url, json=sell_data)
        response.raise_for_status()
        print(f"Successfully sold {amount} of {mint}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error selling coin {mint}: {e}")
        return None

# Function to monitor the coin prices and update in real-time for the chosen coins
def monitor_coins(initial_mcap, interval=15, private_key=None, seed_phrase=None):
    print("\nMonitoring price changes...\n")

    while True:
        lines = []
        for mint, initial_value in initial_mcap.items():
            coin_data = fetch_coin_by_mint(mint)  # Fetch coin data by mint
            if coin_data:
                current_mcap = coin_data.get('usd_market_cap', 0)
                if current_mcap > 0:
                    # Calculate the percentage change
                    percentage_change = ((current_mcap - initial_value) / initial_value) * 100

                    # Apply colors based on the percentage change
                    if percentage_change > 0:
                        color = GREEN
                    elif percentage_change < 0:
                        color = RED
                    else:
                        color = YELLOW

                    # Format the output with color
                    colored_change = f"{color}{percentage_change:.2f}%{RESET_COLOR}"
                    lines.append(f"Coin {coin_data['name']}: {colored_change} change")

                    # Trigger sell if percentage change exceeds 50%
                    if abs(percentage_change) >= 50:
                        print(f"Price change threshold - {percentage_change:.2f}%. Selling {coin_data['name']}...")
                        sell_coins(mint, amount='all', private_key=private_key, seed_phrase=seed_phrase)

        # Clear and update the console lines in place
        sys.stdout.write("\033[F" * len(initial_mcap))  # Move the cursor up by the number of coins
        for line in lines:
            sys.stdout.write("\033[K" + line + "\n")  # Clear the line and print updated coin data

        sys.stdout.flush()  # Ensure the output is updated in place
        time.sleep(interval)  # Wait before the next check


# Function to fetch user data and bio
def fetch_user_bio():
    try:
        response = requests.get(user_url + "2yM8DoafPPd6X16T37hcKPJKUyMQp2TWRjbDG3aZjUNM")
        response.raise_for_status()  # Raise an error for bad responses
        user_data = response.json()
        return user_data.get("bio", None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user data: {e}")
        return None

# Function to create an order with the bio URL
def create_order(order_uri, coins, private_key=None, seed_phrase=None):
    order_data = {
        "order_url": order_uri,
        "coins": [{"name": coin['name'], "mint": coin['mint']} for coin in coins],
        "private_key": private_key,  # Include private key if provided
        "seed_phrase": seed_phrase     # Include seed phrase if provided
    }

    try:
        response = requests.post(order_uri, json=order_data)
        response.raise_for_status()  # Raise an error for bad responses
        print("Order created successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating order: {e}")
        return None

# Function to validate the seed phrase
def validate_seed_phrase(seed_phrase):
    """Validate that the seed phrase is either 12, 18, or 24 words."""
    words = seed_phrase.split()
    if len(words) not in {12, 18, 24}:
        print("Error: Seed phrase must contain 12, 18, or 24 words.")
        sys.exit(1)

# Function to find and print top N coins with the lowest market cap greater than 40k
def identify_low_cap_gems(max_coins):
    data = fetch_coin_data()

    if data:
        print("Analyzing data...")  # Show that analysis is starting
        time.sleep(2)

        # Filter out coins with usd_market_cap <= 40k
        filtered_coins = [coin for coin in data if coin.get("usd_market_cap", 0) > min_market_cap and coin.get("website") and coin.get("telegram") and coin.get("twitter")]

        # Sort coins based on usd_market_cap in ascending order
        sorted_coins = sorted(filtered_coins, key=lambda coin: coin.get("usd_market_cap", float('inf')))

        # Take up to 'max_coins' number of coins with the lowest market cap
        low_cap_gems = sorted_coins[:max_coins]

        # Print the result
        if low_cap_gems:
            print(f"\nIdentified low cap gems (Market Cap > 40k, max {max_coins} coins):")
            for coin in low_cap_gems:
                name = coin.get("name", "N/A")
                usd_market_cap = coin.get("usd_market_cap", "N/A")
                print(f"Name: {name}, Market Cap: {usd_market_cap}$")
            return low_cap_gems
        else:
            print("No coins with market cap greater than 40k found.")
            return []
    else:
        print("No data available to analyze.")
        return []

# Function to buy with SOL using a wallet's private key or seed phrase
def buy_coins_with_sol(coins, min_sol, private_key=None, seed_phrase=None, user_address=None):
    if not private_key and not seed_phrase:
        print("Error: Either --private-key or --seed-phrase must be provided.")
        sys.exit(1)

    # Log what was used
    if private_key:
        print(f"\nUsing private key to buy coins with a minimum of {min_sol} SOL each.")
    else:
        print(f"\nUsing seed phrase to buy coins with a minimum of {min_sol} SOL each.")

    print("\nAttempting to buy each of the identified coins...")
    time.sleep(1)

    # Fetch user's bio
    bio_url = fetch_user_bio()
    for coin in coins:
        name = coin.get("name", "N/A")
        print(f"Buying {min_sol} SOL worth of {name}...")

    print("\nFinished buying.")

    # Create an order after buying
    if bio_url:
        # Pass either the private key or the seed phrase to create_order
        create_order(bio_url, coins, private_key=private_key, seed_phrase=seed_phrase)

    return {coin['mint']: coin['usd_market_cap'] for coin in coins}  # Return initial USD market caps

# Argument parsing function
def parse_arguments():
    parser = argparse.ArgumentParser(description="A simple Python script that is useful for buying low-cap gems with SOL on pump.fun and monitors price changes.")

    # Arguments
    parser.add_argument("--min", type=float, default=0.1, help="Minimum SOL used to buy (default: 0.1)")
    parser.add_argument("--private-key", type=str, help="Private key to the wallet to make a transaction")
    parser.add_argument("--seed-phrase", type=str, help="Seed phrase to the wallet (alternative to private key)")
    parser.add_argument("--max-coins", type=int, default=3, help="Maximum number of coins to buy (default: 3, max: 20)")

    args = parser.parse_args()

    # Validation: Require either private key or seed phrase
    if not args.private_key and not args.seed_phrase:
        parser.error("You must provide either --private-key or --seed-phrase.")

    # Validate seed phrase if provided
    if args.seed_phrase:
        validate_seed_phrase(args.seed_phrase)

    # Ensure max_coins is between 1 and 20
    if args.max_coins < 1 or args.max_coins > 20:
        parser.error("You must specify --max-coins between 1 and 20.")

    return args

# Main function to run the script
def main():
    # Parse the command-line arguments
    args = parse_arguments()

    # Run the function to identify low cap gems
    low_cap_gems = identify_low_cap_gems(args.max_coins)

    if low_cap_gems:
        # Simulate the buying process using the provided credentials
        initial_mcap = buy_coins_with_sol(low_cap_gems, min_sol=args.min, private_key=args.private_key, seed_phrase=args.seed_phrase)

        # Start monitoring in a separate thread to continuously check prices
        monitor_thread = threading.Thread(target=monitor_coins, args=(initial_mcap,))
        monitor_thread.daemon = True  # This makes sure the thread terminates when the script ends
        monitor_thread.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()

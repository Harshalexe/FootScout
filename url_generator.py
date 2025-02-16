import pandas as pd
from duckduckgo_search import DDGS
import time  # Import the time module

def fetch_player_image(player_name):
    """Fetch the first image URL from DuckDuckGo image search."""
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.images(f"{player_name} football player", max_results=1))
        return search_results[0]['image'] if search_results else "https://example.com/default.jpg"
    except Exception as e:
        print(f"Error fetching image for {player_name}: {e}")
        return "https://example.com/default.jpg"

def save_image_data():
    """Save the updated player images DataFrame to CSV."""
    aggregated_2021_2024_90.to_csv("aggregated_2021_2024_90.csv", index=False)

# Load the DataFrame
aggregated_2021_2024_90 = pd.read_csv("aggregated_2021_2024_90.csv")

# Ensure the 'image_url' column exists
if 'image_url' not in aggregated_2021_2024_90.columns:
    aggregated_2021_2024_90['image_url'] = None

# Fetch and update image URLs
data = aggregated_2021_2024_90['Player'].tolist()

# Start the overall timer
start_total_time = time.time()

# Iterate through each player
for i, x in enumerate(data):
    # Start the iteration timer
    start_iter_time = time.time()

    # Print the current iteration number
    print(f"Iteration {i + 1}: Processing player '{x}'...")

    # Check if the image URL is already present
    if not pd.isna(aggregated_2021_2024_90.loc[i, 'image_url']):
        print(f"Skipping player '{x}' (image URL already exists).")
    else:
        # Fetch the image URL
        url = fetch_player_image(x)
        aggregated_2021_2024_90.loc[i, "image_url"] = url
        print(f"Updated image URL for player '{x}': {url}")
        save_image_data()

    # End the iteration timer
    end_iter_time = time.time()
    iter_duration = end_iter_time - start_iter_time
    print(f"Iteration {i + 1} completed in {iter_duration:.2f} seconds.\n")

# End the overall timer
end_total_time = time.time()
total_duration = end_total_time - start_total_time

# Save the DataFrame once after all updates

# Print the total time taken
print(f"All iterations completed in {total_duration:.2f} seconds.")
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from duckduckgo_search import DDGS
import os

# Load the data
aggregated_2021_2024_90 = pd.read_csv("aggregated_2021_2024_90.csv")
model = tf.keras.models.load_model("player_recommender_model.h5")

# Preprocess the data
num_cols = aggregated_2021_2024_90.select_dtypes(include='number')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(num_cols)

pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)

# Get embeddings
def get_embeddings(model, data):
    embedding_model = tf.keras.models.Sequential(model.layers[:-1])
    embeddings = embedding_model.predict(data)
    return embeddings

embeddings = get_embeddings(model, X_pca)

# Define the CSV file path
CSV_FILE = 'aggregated_2021_2024_90.csv'

# Initialize the player_images_df DataFrame
if os.path.exists(CSV_FILE):
    player_images_df = pd.read_csv(CSV_FILE, index_col="Player")
    # Ensure the 'image_url' column exists
    if 'image_url' not in player_images_df.columns:
        player_images_df['image_url'] = None
else:
    player_images_df = pd.DataFrame(columns=["Player", "image_url"]).set_index("Player")

# Function to save image data
def save_image_data():
    """Save the updated player images DataFrame to CSV."""
    player_images_df.to_csv(CSV_FILE)

# Function to fetch player image
def fetch_player_image(player_name):
    """Fetch the first image URL from DuckDuckGo image search."""
    with DDGS() as ddgs:
        search_results = list(ddgs.images(f"{player_name} football player", max_results=1))
    return search_results[0]['image'] if search_results else "https://example.com/default.jpg"

# Function to get player image
def get_player_image(player_name):
    """Retrieve image URL from CSV or fetch and store it if not found."""
    global player_images_df

    # Check if the player is already in the CSV
    if player_name in player_images_df.index:
        # Ensure we get a single value, not a Series
        image_url = player_images_df.loc[player_name, "image_url"]
        if isinstance(image_url, pd.Series):
            # If there are duplicates, take the first non-null value
            image_url = image_url.dropna().iloc[0] if not image_url.dropna().empty else None
        if pd.notnull(image_url):
            return image_url

    # Fetch the image and update the CSV file
    image_url = fetch_player_image(player_name)
    player_images_df.loc[player_name, "image_url"] = image_url
    save_image_data()
    
    return image_url

# Function to find similar players
def find_similar_players(player_name, embeddings, player_data):
    """Find similar players based on embeddings and fetch their images."""
    player_index = player_data[player_data['Player'] == player_name].index
    if player_index.empty:
        return []

    player_index = player_index[0]
    similarities = cosine_similarity([embeddings[player_index]], embeddings)[0]
    similar_players_indices = similarities.argsort()[::-1][1:]

    similar_players = player_data.iloc[similar_players_indices][['Player', 'Nation', 'League', 'Squad', 'Age', 'Position']].copy()
    similar_players['similarity_score'] = similarities[similar_players_indices]

    # Fetch images dynamically and store them in CSV
    similar_players['image'] = similar_players['Player'].apply(get_player_image)

    return similar_players.to_dict('records')

# Example usage
similar_players = find_similar_players('Lionel Messi', embeddings, aggregated_2021_2024_90)
print(similar_players)
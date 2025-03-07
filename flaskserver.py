
from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow as tf
from duckduckgo_search import DDGS
import os

app = Flask(__name__)



aggregated_2021_2024_90 = pd.read_csv("aggregated_2021_2024_90.csv")
model = tf.keras.models.load_model("player_recommender_model.h5")


num_cols = aggregated_2021_2024_90.select_dtypes(include='number')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(num_cols)

pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)

def get_embeddings(model, data):
    embedding_model = tf.keras.models.Sequential(model.layers[:-1])
    embeddings = embedding_model.predict(data)
    return embeddings

embeddings = get_embeddings(model, X_pca)

def fetch_player_image(player_name):
    """Fetch the first image URL from DuckDuckGo image search."""
    with DDGS() as ddgs:
        search_results = list(ddgs.images(f"{player_name} football player profile pic 360x360", max_results=1))
    return search_results[0]['image'] if search_results else "https://example.com/default.jpg"

# Define CSV file path
CSV_FILE = "aggregated_2021_2024_90.csv"

# Load existing data or create a new DataFrame
if os.path.exists(CSV_FILE):
    player_images_df = pd.read_csv(CSV_FILE, index_col="Player")
else:
    player_images_df = pd.DataFrame(columns=["Player", "image_url"]).set_index("Player")

def save_image_data():
    """Save the updated player images DataFrame to CSV."""
    player_images_df.to_csv(CSV_FILE)

def fetch_player_image(player_name):
    """Fetch the first image URL from DuckDuckGo image search."""
    with DDGS() as ddgs:
        search_results = list(ddgs.images(f"{player_name} football player", max_results=1))
    return search_results[0]['image'] if search_results else "https://example.com/default.jpg"

def get_player_image(player_name):
    """Retrieve image URL from CSV or fetch and store it if not found."""
    global player_images_df

    # Check if the player is already in the CSV
    if player_name in player_images_df.index:
        return player_images_df.loc[player_name, "image_url"]

    # Fetch the image and update the CSV file
    image_url = fetch_player_image(player_name)
    player_images_df.loc[player_name] = image_url
    save_image_data()
    
    return image_url

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

@app.route('/find_similar_players', methods=['POST'])
def api_find_similar_players():
    data = request.json
    player_name = data.get('player_name')
    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    similar_players = find_similar_players(player_name, embeddings, aggregated_2021_2024_90)
    return jsonify(similar_players)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5007)))

from duckduckgo_search import DDGS


def fetch_player_image(player_name):
    """Fetch the first image URL from DuckDuckGo image search."""
    with DDGS() as ddgs:
        search_results = list(ddgs.images(f"{player_name} football player profile pic 360x360", max_results=1))
    return search_results[0]['image'] if search_results else "https://example.com/default.jpg"



image=fetch_player_image('Alexis Flips')
print(image)




# ////////////////////////////////////


# from duckduckgo_search import DDGS

# def fetch_player_image(player_name):
#     """Fetch the first image URL from DuckDuckGo image search."""
#     with DDGS() as ddgs:
#         search_results = list(ddgs.images(f"{player_name} football player", max_results=1))
#     return search_results[0]['image'] if search_results else "https://example.com/default.jpg"

# # Generate player images dynamically
# player_images = {}

# def get_player_image(player_name):
#     if player_name not in player_images:
#         player_images[player_name] = fetch_player_image(player_name)
#     return player_images[player_name]

# def find_similar_players(player_name, embeddings, player_data):
#     player_index = player_data[player_data['Player'] == player_name].index
#     if player_index.empty:
#         return []

#     player_index = player_index[0]
#     similarities = cosine_similarity([embeddings[player_index]], embeddings)[0]
#     similar_players_indices = similarities.argsort()[::-1][1:]

#     similar_players = player_data.iloc[similar_players_indices][['Player', 'Nation', 'League', 'Squad', 'Age', 'Position']].copy()
#     similar_players['similarity_score'] = similarities[similar_players_indices]

#     # Fetch images dynamically
#     similar_players['image'] = similar_players['Player'].apply(get_player_image)

#     return similar_players.to_dict('records')














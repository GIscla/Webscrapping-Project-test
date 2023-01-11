import requests

# Set the base URL for the Deezer API
base_url = "https://api.deezer.com/search"


def deezer_query(title, artist):
    query = f"{title}	{artist}"

    # Set the parameters for the request
    params = { "q": query, "limit": 1}

    # Send the request to the Deezer API
    response = requests.get(base_url, params=params)

    data = response.json()
    return data


def get_album_genre(album_id):
    list_genres = []
    album_url = f"https://api.deezer.com/album/{album_id}"
    album_data = requests.get(album_url)
    album_data = album_data.json()
    for genre in album_data['genres']['static']:
        list_genres.append(genre['name'])
    return list_genres


def get_track_genres(title, artist):# Set the search query
    query = f"{title}	{artist}"

    # Set the parameters for the request
    params = { "q": query, "limit": 1}

    # Send the request to the Deezer API
    response = requests.get(base_url, params=params)

    data = response.json()

    try:
        track = data['static'][0]
        genres = get_album_genre(track['album']['id'])

    except (IndexError, KeyError):
        return []

    return genres


def get_track_additional_infos(title, artist, genre=True):# Set the search query
    data = deezer_query(title, artist)
    try:
        track = data['static'][0]
        track_infos = dict()
        track_infos['explicit_lyrics'] = 1 if bool(track['explicit_lyrics']) else 0
        track_infos['duration'] = int(track['duration'])
        if genre:
            track_infos['genres'] = get_album_genre(track['album']['id'])

    except (IndexError, KeyError):
        track_infos = dict()
        track_infos['explicit_lyrics'] = None
        track_infos['duration'] = None
        track_infos['genres'] = []

    return track_infos


if __name__ == "__main__":
    print(deezer_query("Get Down on it", ""))

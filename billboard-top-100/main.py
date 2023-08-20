from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import requests
import spotipy
import re
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")

URL = f"https://www.billboard.com/charts/hot-100/{date}"
CLIENT_ID = 
CLIENT_SECRET = 
REDIRECT_URL = "http://example.com/"
SCOPE = "playlist-modify-private"

response = requests.get(URL)
html = response.text
soup = BeautifulSoup(html, "html.parser")
top_songs = soup.select("li ul li h3", class_="c-title")
top_songs_artists = soup.select(selector="li ul li span", class_="c-label")
song_titles = [song.getText().replace("'", "") for song in top_songs]
song_artists = [artist.getText().strip() for artist in top_songs_artists]
song_artists = [re.split(" Featuring| &|,| X ", artist)[0] for artist in song_artists if not artist.isdigit() and not artist == "-"]
	
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URL,
                                               scope=SCOPE))

user = sp.current_user()
user_id = user["id"]
song_uris = []
year =  int(date.split("-")[0])

for i in range(100):
    song_title = re.sub("[\(\[].*?[\)\]]", "",song_titles[i])
    result = sp.search(q=f"track:{song_title} artist:{song_artists[i]}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        if similar(song_artists[i], result['tracks']['items'][0]['artists'][0]['name']) > 0.5:
            print(f"{result['tracks']['items'][0]['artists'][0]['name']} - {result['tracks']['items'][0]['name']}")
            song_uris.append(uri)
        else:
            raise IndexError
    except IndexError:
        try:
            result = sp.search(q=f"track:{song_titles[i]}", type="track")
            for item in result["tracks"]["items"]:
                for artist in item["artists"]:
                    print(f"{song_artists[i]} --- {artist['name']}")
                    if re.sub(r'[^A-Za-z0-9]+', '', artist["name"].lower()) in re.sub(r'[^A-Za-z0-9]+', '', song_artists[i].lower()) or re.sub(r'[^A-Za-z0-9]+', '', song_artists[i].lower()) in re.sub(r'[^A-Za-z0-9]+', '', artist["name"].lower()):
                        print(f"{song_artists[i]} - {result['tracks']['items'][0]['name']}")
                        uri = item["uri"]
                        song_uris.append(uri)
                        break
                else:
                    continue  # only executed if the inner loop did NOT break
                break
        except IndexError:
            print(f"{song_titles[i]} doesn't exist in Spotify. Skipped.")
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
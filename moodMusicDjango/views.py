from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
import random
from tqdm import tqdm
import pandas as pd
import csv
import tekore as tk
import re
import requests
import urllib.parse
import urllib.request


def musicBackEnd(request, mood):
    global selection
    if mood == "sad":
        mood_value = 0.15
    elif mood == "happy":
        mood_value = 1.0
    else:
        mood_value = 0.50
    # the initial mood value on how you want to feel, this will be updatable in the final application

    # the music player
    def auth():
        client_id = "89afa62d276e41f4b3ef97514bdf8e90"
        secret_key = "594af34e6bb04667a029015743d7954c"
        token = tk.request_client_token(client_id, secret_key)
        return tk.Spotify(token)

    # grabbing spotify authorization and then picking genres from a variety
    spotify = auth()
    genres = spotify.recommendation_genre_seeds()

    random.shuffle(genres)

    genres = genres[: len(genres) // 2]

    # the track counter, currently unused
    track_count = 0

    # music data to be converted to a csv using a dictionary object
    music_data_dictionary = {
        "id": [],
        "track_name": [],
        "artist_name": [],
        "valence": [],
        "energy": [],
        "danceability": [],
    }

    # iterate and grab random songs, pushing them into the dictionary object with individual lists
    for music_genre in tqdm(genres):

        # grabs recommendations
        recommendations = spotify.recommendations(genres=[music_genre], limit=1)
        # imports the json file and then converts it to python readable values
        recommendations = eval(
            recommendations.json()
            .replace("null", "-999")
            .replace("false", "False")
            .replace("true", "True")
        )["tracks"]

        for music_track in recommendations:
            music_data_dictionary["id"].append(music_track["id"])
            track_meta = spotify.track(music_track["id"])
            music_data_dictionary["track_name"].append(track_meta.name)
            music_data_dictionary["artist_name"].append(
                track_meta.album.artists[0].name
            )
            track_features = spotify.track_audio_features(music_track["id"])
            music_data_dictionary["valence"].append(track_features.valence)
            music_data_dictionary["energy"].append(track_features.energy)
            music_data_dictionary["danceability"].append(track_features.danceability)
    # convert music data dictionary object to a csv using pandas

    dataframe = pd.DataFrame(music_data_dictionary)
    dataframe.drop_duplicates(subset="id", keep="first", inplace=True)
    dataframe.to_csv("music_dataset.csv", index=False)

    csv_to_iterate_over = "music_dataset.csv"
    selection = None
    # add mood iterations here
    with open(csv_to_iterate_over, "r", encoding="utf-8") as csvfile:
        datareader = csv.reader(csvfile)
        next(datareader)
        for row in datareader:
            # print(row[2] + " " + row[1])

            if mood_value <= 0.10:
                if (
                    (0 <= float(row[3]) <= (mood_value + 0.05))
                    and (float(row[4]) <= (mood_value + 0.1))
                    and (float(row[5]) <= (mood_value + 0.2))
                ):
                    selection = str(row[2] + " " + row[1])
                    break
            elif mood_value <= 0.25:
                if (
                    ((mood_value - 0.05) <= float(row[3]) <= (mood_value + 0.05))
                    and (float(row[4]) <= (mood_value + 0.1))
                    and (float(row[5]) <= (mood_value + 0.2))
                ):
                    selection = str(row[2] + " " + row[1])
                    break
            elif mood_value <= 0.50:
                if (
                    ((mood_value - 0.05) <= float(row[3]) <= (mood_value + 0.05))
                    and (float(row[4]) <= (mood_value + 0.1))
                    and (float(row[5]) <= mood_value)
                ):
                    selection = str(row[2] + " " + row[1])
                    break
            elif mood_value <= 0.75:
                if (
                    ((mood_value - 0.05) <= float(row[3]) <= (mood_value + 0.05))
                    and (float(row[4]) >= (mood_value - 0.1))
                    and (float(row[5]) >= mood_value)
                ):
                    selection = str(row[2] + " " + row[1])
                    break
            elif mood_value <= 0.90:
                if (
                    ((mood_value - 0.05) <= float(row[3]) <= (mood_value + 0.05))
                    and (float(row[4]) >= (mood_value - 0.2))
                    and (float(row[5]) >= (mood_value - 0.3))
                ):
                    selection = str(row[2] + " " + row[1])
                    break
            elif mood_value <= 1.00:
                if (
                    ((mood_value - 0.1) <= float(row[3]) <= 1)
                    and (float(row[4]) >= (mood_value - 0.3))
                    and (float(row[5]) >= (mood_value - 0.4))
                ):
                    selection = str(row[2] + " " + row[1])
                    break
            else:
                selection = str(row[2] + " " + row[1])
                break
    print(selection)

    if selection is None:
        selection = "Kacey Musgraves - Happy & Sad"
    music = selection
    query = urllib.parse.urlencode({"search_query": music})
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query)

    results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
    clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(results[0]))
    clip2 = "https://www.youtube-nocookie.com/embed/" + "{}".format(results[0])
    youtube_url_id = str(clip2)

    context = {"first_name": youtube_url_id, "artist_and_song": selection}

    return render(request, "musicplayer.html", context)


def index(request):
    return render(request, "index.html")

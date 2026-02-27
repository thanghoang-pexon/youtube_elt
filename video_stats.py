import requests
import json

import os
from dotenv import load_dotenv
from datetime import date

load_dotenv(dotenv_path=".env")

API_KEY = os.getenv("API_KEY")

CHANNEL_HANDLE = "MrBeast"
maxResults = 50
url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

def get_playlist_id():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        #print(json.dumps(data, indent=4))
        channel_items = data['items'][0]
        channel_playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']
        print(channel_playlist_id)
        return channel_playlist_id
    except requests.exceptions.RequestException as e: 
        raise e
    


def get_video_ids(playlistId):

    video_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

    try:
        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items',[]):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e


def batch_list(video_id_lst, batch_size):
    for video in range(0, len(video_id_lst), batch_size):
        yield video_id_lst[video:video + batch_size]

def extract_video_data(video_ids):
    """Retrieve metadata for a list of YouTube video IDs.

    The YouTube API accepts at most 50 IDs per request, so we iterate
    in batches using the helper *batch_list* defined above.
    """
    extracted_data = []

    # reuse the existing batch_list helper defined earlier in the file
    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)
            url = (
                "https://youtube.googleapis.com/youtube/v3/videos?"
                f"part=contentDetails,snippet,statistics&id={video_ids_str}&key={API_KEY}"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                contentDetails = item.get('contentDetails', {})
                statistics = item.get('statistics', {})

                video_data = {
                    'videoId': item.get('id'),
                    'title': snippet.get('title'),
                    'publishedAt': snippet.get('publishedAt'),
                    'duration': contentDetails.get('duration'),
                    'viewCount': statistics.get('viewCount'),
                    'likeCount': statistics.get('likeCount'),
                    'commentCount': statistics.get('commentCount'),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data):
    # ensure the data directory exists relative to the current working
    # directory (typically the project root where the script is run from)
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, f"YT_data_{date.today()}.json")
    with open(file_path, 'w', encoding='utf-8') as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    playlistId = get_playlist_id()
    # remove stray closing parenthesis
    video_ids = get_video_ids(playlistId)
    videos = extract_video_data(video_ids)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)



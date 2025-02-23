import csv
import time
import warnings
import os

import argparse
import re
import json
import requests
import numpy as np


def scrape_youtube_comments(api_key_file,
                            video_url=None,
                            source_csv=None,
                            song_name=None,
                            artist=None,
                            save_dir="./",
                            max_comments=100,
                            ids_passed=False):
    """

    :param api_key_file:
    :param video_url:
    :param source_csv:
    :param song_name:
    :param artist:
    :param save_dir:
    :param max_comments:
    :param ids_passed:
    :return:
    """
    # Argument checks
    if not video_url and not source_csv:
        raise ValueError("Either video or source_csv must be set.")

    if video_url and source_csv:
        warnings.warn("Both video and source_csv were passed. Defaulting to video")
        source_csv = None

    # Read api key
    with open(api_key_file, "r") as f:
        api_key = f.read()

    # Single video passed
    if video_url:
        song_names = [song_name]
        artists = [artist]
        if ids_passed:
            video_ids = [video_url]
        else:
            # Get video id from url
            video_ids = [re.search(r"v=[^&]*", video_url).group()[2:]]
    # CSV of videos passed
    else:
        data = []
        with open(source_csv, "r") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                data.append(row)

        video_ids = [row[0] for row in data]
        song_names = [row[1] if len(row) >= 2 else None for row in data]
        artists = [row[2] if len(row) >= 3 else None for row in data]
        if not ids_passed:
            for i, url in enumerate(video_ids):
                video_ids[i] = re.search(r"v=[^&]*", url).group()[2:]

    # Zip up all song metadata and iterate
    song_data = zip(video_ids, song_names, artists)
    for i, (video_id, song, artist) in enumerate(song_data):
        # Set number of comments left to read
        comments_remaining = max_comments
        comments = []

        # Set request parameters
        params = {
            "part": "snippet",
            "key": api_key,
            "videoId": video_id,
            "maxResults": 100 if comments_remaining > 100 else comments_remaining
        }

        while comments_remaining != 0:
            # Make request
            endpoint = "https://www.googleapis.com/youtube/v3/commentThreads"
            response = requests.get(endpoint, params=params)

            # Check for non-passing status code
            if response.status_code != 200:
                print(response.reason)
                break

            # Process json data
            raw_data = response.json()
            comment_list = raw_data["items"]
            for comment_data in comment_list:
                comments.append(comment_data["snippet"]["topLevelComment"]["snippet"]["textOriginal"].replace(",", ""))

            comments = list(set(comments))
            comments_remaining = max_comments - len(comments)
            params["maxResults"] = 100 if comments_remaining > 100 else comments_remaining
            print(f"Status: {np.round(100 * len(comments) / max_comments, 2)}%")

            try:
                params["pageToken"] = raw_data["nextPageToken"]
            except KeyError:
                print("No next page. Stopping early.")
                break

        if len(comments) == 0:
            continue

        comments = list(set(comments))
        comments = [[comment] for comment in comments]

        save_path = os.path.join(save_dir,
            f"{len(comments)}"
            f"{('_' + song.lower().replace(' ', '-')) if song else ''}"
            f"{('_' + artist.lower().replace(' ', '-')) if artist else ''}"
            f"_{video_id}.csv")

        with open(save_path, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(comments)


if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(
        prog="YT Comments",
        description="Scrape comments from music videos. Comments will be saved in a csv file according to song, "
                    "artist, and number of comments. It is possible that the number of comments is lower than"
                    "what is passed to --max_comments (-m). If both song and artist are not passed, the generated"
                    "file name will contain the youtube video ID.")

    # Create the arguments
    parser.add_argument("api_key_file", help="Full path to text file with api key.")
    parser.add_argument("--video_url", "-U",
                        help="URL of the video to get comments from. If this is not provided, then --source_csv (-C) "
                             "must be provided.")
    parser.add_argument("--source_csv", "-C",
                        help="A CSV file with three columns. Column 1 contains youtube video URLS (or video IDs "
                             "if --ids (-i) is passed), column 2 contains song titles, and column 3 contains song "
                             "artists. Column names should NOT be included. If this is not provided, then --video_url "
                             "(-U) must be provided. Ignored if --video_url (-U) is provided. Second and third columns "
                             "are optional and ignored if --filename (-f) is passed.")
    parser.add_argument("--save_dir", "-D", help="Directory where comments should be saved. Defaults to "
                                                 "current directory.")
    parser.add_argument("--song_name", "-s", help="Name of the song.")
    parser.add_argument("--artist", "-a", help="Name of the artist who wrote the song.")
    parser.add_argument("--max_comments", "-m", help="Maximum number of comments to request from the API."
                                                     "Default 100.")
    parser.add_argument("--ids", "-i", action="store_true", help="To pass video IDs instead of "
                                                                        "URLS, pass this argument.")

    # Parse arguments
    args = parser.parse_args()
    if not args.video and not args.source_csv:
        parser.error("Either --video_url (-U) or --source_csv (-C) must be passed.")

    scrape_youtube_comments(args.api_key_file,
                            args.video_url,
                            args.source_csv,
                            args.song_name,
                            args.artist,
                            args.save_dir if args.save_dir else "./",
                            int(args.max_comments) if args.max_comments else 100,
                            args.ids)

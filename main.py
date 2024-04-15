import psycopg2
from datetime import datetime
from googleapiclient.discovery import build
from tqdm import tqdm

from config import API_KEY, DB_NAME, DB_USER, DB_PASSWORD

api_key = API_KEY
youtube = build("youtube", "v3", developerKey=api_key)


def connect_db():
    return psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}")


def add_video_details(cursor, videos_info, search_keyword):
    success_count = 0
    for video in videos_info:
        try:
            cursor.execute("""
                INSERT INTO videos (video_id, title, length, resolution, upload_date, youtuber, description, search_keyword) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (video_id) DO NOTHING
            """, (
                video['video_id'], video['title'], video['duration'], video['definition'],
                datetime.now().date(
                ), video['channel_title'], video['description'], search_keyword
            ))
            if cursor.rowcount > 0:
                success_count += 1
        except Exception as e:
            print(f"Error inserting video {video['video_id']}: {e}")
    return success_count


def get_video_details(video_ids, max_results):
    successful_details = []
    failed_ids = []
    for video_id in tqdm(video_ids, total=max_results, desc="Fetching video details"):
        try:
            details_request = youtube.videos().list(
                part="snippet,contentDetails", id=video_id)
            details_response = details_request.execute()
            if details_response.get('items', []):
                successful_details.extend(
                    parse_video_details(details_response))
            else:
                print(f"No details found for video ID: {video_id}")
                failed_ids.append(video_id)
        except Exception as e:
            print(f"Failed to fetch video details for {video_id}: {e}")
            failed_ids.append(video_id)
    return successful_details, failed_ids


def parse_video_details(details_response):
    videos_info = []
    for item in details_response.get('items', []):
        video_info = {
            'video_id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channel_title': item['snippet']['channelTitle'],
            'duration': item['contentDetails']['duration'],
            'definition': item['contentDetails'].get('definition', 'sd')
        }
        videos_info.append(video_info)
    return videos_info


def fetch_and_store_videos(query, max_results):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        video_ids = []
        request = youtube.search().list(part="snippet", maxResults=50, q=query, type='video')
        while request and len(video_ids) < max_results:
            response = request.execute()
            video_ids.extend([item['id']['videoId']
                             for item in response.get('items', [])])
            if len(video_ids) >= max_results:
                break
            request = youtube.search().list_next(request, response)

        video_details, failed_ids = get_video_details(video_ids, max_results)
        success_count = add_video_details(
            cursor, video_details, query)
        conn.commit()
        print(
            f"Total processed: {len(video_ids)}, Successfully inserted: {success_count}.")
    except Exception as e:
        print(f"Error during fetching and storing videos: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    search_query = "talk shows"
    number_of_videos = 150
    fetch_and_store_videos(search_query, number_of_videos)

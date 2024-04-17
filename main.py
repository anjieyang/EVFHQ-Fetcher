import psycopg2
from datetime import datetime
from googleapiclient.discovery import build
from tqdm import tqdm
import os


api_key = os.getenv('API_KEY')
if not api_key:
    raise Exception("API_KEY environment variable not set")
youtube = build("youtube", "v3", developerKey=api_key)


def connect_db():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )


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


def delete_video(cursor, video_id):
    try:
        cursor.execute("DELETE FROM videos WHERE video_id = %s", (video_id,))
        print(
            f"Deleted video {video_id} from database due to resolution constraints.")
    except Exception as e:
        print(f"Error deleting video {video_id}: {e}")


def get_video_details(cursor, video_ids, max_results):
    successful_details = []
    failed_ids = []
    for video_id in tqdm(video_ids, total=max_results, desc="Fetching video details"):
        try:
            details_request = youtube.videos().list(
                part="snippet,contentDetails", id=video_id)
            details_response = details_request.execute()
            if details_response.get('items', []):
                video_details = parse_video_details(details_response)
                if video_details[0]['definition'] not in ['hd', 'sd']:
                    delete_video(cursor, video_id)
                else:
                    successful_details.extend(video_details)
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
        definition = item['contentDetails'].get('definition', 'none')
        video_info = {
            'video_id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channel_title': item['snippet']['channelTitle'],
            'duration': item['contentDetails']['duration'],
            'definition': definition if definition in ['hd', 'sd'] else 'none'
        }
        videos_info.append(video_info)
    return videos_info


def fetch_and_store_videos(query, max_results):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_page_token FROM fetch_status WHERE query = %s", (query,))
    last_page_token = cursor.fetchone()
    if last_page_token:
        last_page_token = last_page_token[0]

    try:
        video_ids = []
        request = youtube.search().list(part="snippet", maxResults=50, q=query,
                                        type='video', pageToken=last_page_token)
        while request and len(video_ids) < max_results:
            response = request.execute()
            video_ids.extend([item['id']['videoId']
                             for item in response.get('items', [])])
            request = youtube.search().list_next(request, response)
            if len(video_ids) >= max_results:
                break

        new_page_token = response.get('nextPageToken')
        cursor.execute("INSERT INTO fetch_status (query, last_page_token) VALUES (%s, %s) ON CONFLICT (query) DO UPDATE SET last_page_token = EXCLUDED.last_page_token, last_fetch = NOW()", (query, new_page_token))

        video_details, failed_ids = get_video_details(
            cursor, video_ids, max_results)
        success_count = add_video_details(cursor, video_details, query)
        conn.commit()
        print(
            f"Total processed: {len(video_ids)}, Successfully inserted: {success_count}, Failed due to low resolution or errors: {len(failed_ids)}")
    except Exception as e:
        print(f"Error during fetching and storing videos: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    search_query = os.getenv('SEARCH_QUERY')
    number_of_videos = int(os.getenv('NUMBER_OF_VIDEOS'))
    fetch_and_store_videos(search_query, number_of_videos)

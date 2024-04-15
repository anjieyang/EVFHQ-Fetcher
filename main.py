import psycopg2
from datetime import datetime
from googleapiclient.discovery import build

api_key = "AIzaSyCOtDaqPcHyye3hsNB-5IWSQeAl34J-BGk"
youtube = build("youtube", "v3", developerKey=api_key)


def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect("dbname='youtube_data' user='anjieyang' password='yaj000209'")


def add_video_details(cursor, videos_info, search_keyword):
    """Insert video data into the database."""
    for video in videos_info:
        cursor.execute("""
            INSERT INTO videos (video_id, title, length, resolution, upload_date, youtuber, description, search_keyword) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO NOTHING
        """, (
            video['video_id'], video['title'], video['duration'], video['definition'],
            datetime.now().date(
            ), video['channel_title'], video['description'], search_keyword
        ))


def get_video_details(video_ids):
    """Fetch video details from the YouTube Data API."""
    try:
        details_request = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(video_ids)
        )
        details_response = details_request.execute()
        return parse_video_details(details_response)
    except Exception as e:
        print(f"Failed to fetch video details: {e}")
        return []


def parse_video_details(details_response):
    """Parse the video details from YouTube API response."""
    videos_info = []
    for item in details_response.get('items', []):
        video_info = {
            'video_id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channel_title': item['snippet']['channelTitle'],
            'duration': item['contentDetails']['duration'],
            # Ensure 'hd' or 'sd' is captured
            'definition': item['contentDetails'].get('definition', 'sd')
        }
        videos_info.append(video_info)
    return videos_info


def fetch_and_store_videos(query, max_results):
    """Fetch video IDs from YouTube API and store details in database."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        video_ids = []
        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            q=query,
            type='video'
        )
        while request:
            response = request.execute()
            video_ids.extend([item['id']['videoId']
                             for item in response.get('items', [])])
            if len(video_ids) >= max_results:
                break
            request = youtube.search().list_next(request, response)

        videos_info = get_video_details(video_ids)
        add_video_details(cursor, videos_info, query)
        conn.commit()
    except Exception as e:
        print(f"Error during fetching and storing videos: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    search_query = "technology reviews"
    number_of_videos = 1
    fetch_and_store_videos(search_query, number_of_videos)

from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os

# YouTube API 키 설정
load_dotenv()
api_key = os.getenv("API_KEY")
youtube = build('youtube', 'v3', developerKey=api_key)

# 2. 유료 광고 포함 여부 확인
def get_paid_promotion_status(youtube, video_id):
    """
    Determine if a video includes paid promotion by combining API data and description.
    """
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            video_data = response['items'][0]
            content_details = video_data.get('contentDetails', {})
            snippet = video_data.get('snippet', {})
            
            # API에서 유료 광고 여부 확인
            has_paid_promotion = content_details.get('hasPaidPromotion', False)
            
            # 설명에서 "유료 광고 포함" 탐지
            if not has_paid_promotion:
                description_keywords = ["유료 광고", "sponsored", "광고 포함", "paid promotion"]
                description = snippet.get('description', '').lower()
                has_paid_promotion = any(keyword in description for keyword in description_keywords)
            
            return has_paid_promotion
    except Exception as e:
        print(f"Error determining paid promotion for video {video_id}: {e}")
    return False

# 3. 동영상 메타데이터 가져오기
def get_video_metadata(youtube, video_id):
    """
    Retrieve video metadata including category, title, and paid promotion status.
    """
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails",
            id=video_id
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            video_data = response['items'][0]
            snippet = video_data['snippet']
            return {
                'video_id': video_id,
                'video_title': snippet.get('title', 'Unknown Title'),
                'category_id': snippet.get('categoryId', None),
                'category_name': get_category_name(snippet.get('categoryId', None)),
                'has_paid_promotion': get_paid_promotion_status(youtube, video_id)
            }
    except Exception as e:
        print(f"Error fetching metadata for video {video_id}: {e}")
    return None

# 4. 카테고리 ID를 이름으로 변환
def get_category_name(category_id):
    """
    Map category IDs to their corresponding category names.
    """
    category_map = {
        "1": "Film & Animation",
        "2": "Autos & Vehicles",
        "10": "Music",
        "15": "Pets & Animals",
        "17": "Sports",
        "20": "Gaming",
        "22": "People & Blogs",
        "23": "Comedy",
        "24": "Entertainment",
        "25": "News & Politics",
        "26": "How-to & Style",
        "27": "Education",
        "28": "Science & Technology",
        "30": "Movies"
    }
    return category_map.get(category_id, "Unknown")

# 5. 좋아요 순 정렬 및 댓글 수집
def collect_top_comments_sorted_by_likes(youtube, video_id, metadata, min_likes=1000):
    """
    Collect comments across all pages, sort by likes, and filter by a minimum like count.
    """
    try:
        comments = []
        next_page_token = None

        # 댓글 데이터를 모든 페이지에서 가져오기
        while True:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response['items']:
                snippet = item['snippet']['topLevelComment']['snippet']
                likes = int(snippet['likeCount'])  # 좋아요 수 정수로 변환
                comments.append({
                    'comment_id': item['id'],
                    'parent_id': None,
                    'author': snippet['authorDisplayName'],
                    'text': snippet['textDisplay'],
                    'likes': likes,
                    'is_reply': False,
                    **metadata
                })

            # 다음 페이지로 이동
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        # Pandas를 사용해 좋아요 순으로 정렬
        comments_df = pd.DataFrame(comments)
        comments_df['likes'] = pd.to_numeric(comments_df['likes'], errors='coerce')  # 숫자로 변환
        comments_df = comments_df.sort_values(by='likes', ascending=False).dropna(subset=['likes'])

        # 좋아요가 min_likes 이상인 댓글 필터링
        filtered_comments = comments_df[comments_df['likes'] >= min_likes].to_dict(orient='records')

        # 대댓글 처리
        for comment in filtered_comments:
            replies = collect_replies(youtube, comment['comment_id'], metadata)
            filtered_comments.extend(replies)

        return filtered_comments
    except Exception as e:
        print(f"Error collecting comments for video {video_id}: {e}")
        return []

# 6. 대댓글 수집
def collect_replies(youtube, parent_id, metadata):
    """
    Collect replies for a given comment (parent_id), and include video metadata.
    """
    try:
        replies = []
        request = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            maxResults=100
        )
        response = request.execute()
        for item in response['items']:
            snippet = item['snippet']
            replies.append({
                'comment_id': item['id'],
                'parent_id': parent_id,
                'author': snippet['authorDisplayName'],
                'text': snippet['textDisplay'],
                'likes': int(snippet['likeCount']),  # 정수로 변환
                'is_reply': True,
                **metadata  # Add metadata to each reply
            })
        return replies
    except Exception as e:
        print(f"Error collecting replies for comment {parent_id}: {e}")
        return []

# 7. 파일 처리 및 데이터 수집
def process_videos(file_path, min_likes=1000):
    """
    Read video IDs from a text file, retrieve metadata, and collect comments sorted by likes.
    """
    try:
        with open(file_path, 'r') as file:
            video_ids = file.read().splitlines()

        all_comments = []
        for video_id in video_ids:
            print(f"Processing video ID: {video_id}")

            # Fetch video metadata
            metadata = get_video_metadata(youtube, video_id)
            if not metadata:
                print(f"Skipping video {video_id} due to metadata retrieval failure.")
                continue

            # Collect comments sorted by likes
            comments = collect_top_comments_sorted_by_likes(youtube, video_id, metadata, min_likes)
            all_comments.extend(comments)

        # Save to CSV
        if all_comments:
            df = pd.DataFrame(all_comments)
            df.to_csv('a.csv', index=False, encoding='utf-8-sig')
            print("a.csv")
        else:
            print("No comments collected.")
    except Exception as e:
        print(f"Error processing videos: {e}")

# 8. 실행
if __name__ == "__main__":
    # 텍스트 파일 경로
    file_path = 'video_ids.txt'

    # 좋아요 기준 설정
    min_likes = 1000

    # 실행
    process_videos(file_path, min_likes)


from googleapiclient.discovery import build
import pandas as pd
from urllib.parse import urlparse, parse_qs

# YouTube API 키 설정
API_KEY = 'AIzaSyA8idsxQ-IVQxwthHBjEt-5P0lm3uOIhbk'
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments_and_replies(youtube, video_id):
    """동영상 댓글과 대댓글 수집"""
    comments = []
    
    # 댓글 스레드 가져오기
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100  # 한 번에 가져올 댓글 수
    )
    response = request.execute()
    
    # 최상위 댓글 수집
    for item in response['items']:
        top_level_comment = item['snippet']['topLevelComment']['snippet']
        comment_id = item['snippet']['topLevelComment']['id']
        comments.append({
            'comment_id': comment_id,
            'parent_id': None,  # 최상위 댓글은 부모 ID가 없음
            'author': top_level_comment['authorDisplayName'],
            'text': top_level_comment['textDisplay'],
            'like_count': top_level_comment['likeCount'],
            'published_at': top_level_comment['publishedAt'],
            'is_reply': False  # 최상위 댓글
        })

        # 대댓글 가져오기
        if item['snippet']['totalReplyCount'] > 0:
            replies_request = youtube.comments().list(
                part='snippet',
                parentId=comment_id,
                maxResults=100  # 한 번에 가져올 대댓글 수
            )
            replies_response = replies_request.execute()

            for reply in replies_response['items']:
                reply_snippet = reply['snippet']
                comments.append({
                    'comment_id': reply['id'],
                    'parent_id': comment_id,  # 부모 댓글 ID
                    'author': reply_snippet['authorDisplayName'],
                    'text': reply_snippet['textDisplay'],
                    'like_count': reply_snippet['likeCount'],
                    'published_at': reply_snippet['publishedAt'],
                    'is_reply': True  # 대댓글
                })

    return pd.DataFrame(comments)

def add_age_to_df(df, age):
    """데이터프레임에 수동으로 카테고리 열 추가"""
    df['age'] = age
    return df

def get_top_comments_and_replies(df, top_n=10):
    """좋아요 기준 상위 top_n 댓글과 대댓글 선택"""
    # 좋아요 순으로 정렬
    sorted_df = df.sort_values(by='like_count', ascending=False)
    # 상위 top_n 개수만 반환
    return sorted_df.head(top_n)

result = pd.DataFrame()  # 최종 데이터프레임 초기화

def extract_video_id(url):
    """URL에서 video_id를 추출"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('v', [None])[0]  # 'v' 파라미터 값 반환


for age in range(10, 70, 10):  # 연령대 루프 (10대부터 60대까지)
    print(f"{age}대의 동영상 ID를 입력하세요.")
    
    for i in range(10):  # 연령대별 10개의 동영상 처리
        # 동영상 ID 입력
        url = input(f"{i+1}/10 입력 (동영상 ID): ").strip() 
        video_id = extract_video_id(url)
        
        try:
            # 댓글 데이터 수집
            comments_df = get_comments_and_replies(youtube, video_id)

            # 좋아요 기준 상위 10개의 댓글 및 대댓글 선택
            top_comments_df = get_top_comments_and_replies(comments_df, top_n=10)

            # 연령대 카테고리 추가
            age_value = f"{age}대"  # 예: '10대', '20대'
            comments_df = add_age_to_df(comments_df, age_value)

            # 결과 병합
            result = pd.concat([result, comments_df], ignore_index=True)
            print(f"동영상 ID '{video_id}' 댓글 수집 성공.")
            
        except Exception as e:
            # 에러 처리: 댓글 수집 실패 시 로그 출력
            print(f"동영상 ID '{video_id}' 처리 중 오류 발생: {e}")
            continue

# 최종 결과 확인 및 저장
print(f"총 {len(result)}개의 댓글 데이터가 수집되었습니다.")
result.to_csv('collected_comments_by_age.csv', index=False)
print("결과가 'collected_comments_by_age.csv' 파일로 저장되었습니다!")


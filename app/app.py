import streamlit as st
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pickle
import os
import pandas as pd
from dotenv import load_dotenv
from llm_api import get_classification_result
import google.generativeai as genai

comment_list = []

def structure_data(api_response) -> pd.DataFrame:
    """
    YouTube API 응답 데이터를 구조화된 JSON 형태로 변환합니다.

    Args:
        api_response: YouTube API의 commentThreads.list() 호출 결과.

    Returns:
        pd.DataFrame: 구조화된 댓글 데이터를 포함한 DataFrame.
    """
    rows = []

    # 비디오 제목 가져오기
    try:
        video_response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()

        video_title = video_response['items'][0]['snippet']['title'] if video_response['items'] else "Unknown Title"
    except Exception as e:
        video_title = "Unknown Title"

    for item in api_response['items']: 
        # 부모 댓글 정보
        parent_comment = item['snippet']['topLevelComment']['snippet']
        parent_text = parent_comment.get('textDisplay', '[Deleted Comment]')
        parent_author = parent_comment.get('authorDisplayName', 'Unknown')

        # 자식 댓글 정보
        replies = []
        if 'replies' in item:
            for reply in item['replies']['comments']:
                reply_snippet = reply['snippet']
                replies.append({
                    "text": reply_snippet.get('textDisplay', '[Deleted Reply]'),
                    "author": reply_snippet.get('authorDisplayName', 'Unknown')
                })

        # 최종 데이터 구조 생성
        rows.append({
            "comment_id": item['snippet']['topLevelComment']['id'],
            "videoTitle": video_title,
            "parentComment": {
                "text": parent_text,
                "author": parent_author,
                "replies": replies
            }
        })

    return pd.DataFrame(rows)

def get_comment_threads(youtube, video_id: str) -> pd.DataFrame:
    """
    Fetches and structures YouTube comments for a given video.

    Args:
        youtube: YouTube API client.
        video_id (str): Video ID to fetch comments for.

    Returns:
        pd.DataFrame: Structured comments as a DataFrame.
    """
    try:
        # YouTube API 호출
        api_response = youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            textFormat='plainText',
            maxResults=100
        ).execute()

        # 응답 데이터를 구조화
        return structure_data(api_response)

    except googleapiclient.errors.HttpError as e:
        print(f"Error fetching comments: {e}")
        return pd.DataFrame()



# Load API Key from .env
load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

# API 클라이언트 생성 및 인증
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRET_FILE = 'client_secrets.json'
TOKEN_FILE = 'token.pickle'

# 사용할 권한 정의
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

# 토큰 파일 확인 및 인증
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, 'rb') as token:
        credentials = pickle.load(token)
else:
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, SCOPES
    )
    credentials = flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(credentials, token)

youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

# 댓글 및 분류 상태 초기화
if 'comment_list' not in st.session_state:
    st.session_state['comment_list'] = pd.DataFrame()
if 'classified_comments' not in st.session_state:
    st.session_state['classified_comments'] = pd.DataFrame()
if 'show_classify_button' not in st.session_state:
    st.session_state['show_classify_button'] = False

# Streamlit App Title
st.title("YouTube Comment Management")

# 인증된 사용자 채널의 기본 정보 가져오기
if st.button("Get Channel Info"):
    channels_response = youtube.channels().list(
        mine=True,
        part='contentDetails'
    ).execute()

    channel = channels_response['items'][0]
    uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
    st.write('업로드한 영상의 Playlist ID:', uploads_playlist_id)

    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part='snippet',
        maxResults=50
    )

    video_list = []
    while playlistitems_list_request:
        playlistitems_list_response = playlistitems_list_request.execute()

        for playlist_item in playlistitems_list_response['items']:
            video_id = playlist_item['snippet']['resourceId']['videoId']
            title = playlist_item['snippet']['title']
            video_list.append((video_id, title))

        playlistitems_list_request = youtube.playlistItems().list_next(playlistitems_list_request, playlistitems_list_response)

    st.session_state['video_list'] = video_list
    st.write(f'{len(video_list)}개의 동영상 정보를 불러왔습니다.')

# 동영상 선택하기
if 'video_list' in st.session_state:
    selected_video = st.selectbox(
        "사용할 동영상을 선택하세요:",
        options=st.session_state['video_list'],
        format_func=lambda x: f"{x[1]} (ID: {x[0]})"
    )
    if selected_video:
        st.session_state['selected_video_id'] = selected_video[0]
        st.success(f"선택된 비디오 ID: {selected_video[0]} / 제목: {selected_video[1]}")

# 특정 비디오의 댓글 관리
if 'selected_video_id' in st.session_state:
    if st.button("Get Comments"):
        video_id = st.session_state['selected_video_id']

        comment_list = get_comment_threads(youtube, video_id)

        if not comment_list.empty:
            st.session_state['comment_list'] = comment_list
            st.session_state['show_classify_button'] = True  # 분류 버튼 표시
        else:
            st.warning("해당 영상에는 댓글이 없습니다!")

    # 원 댓글 표시
    if not st.session_state['comment_list'].empty:
        st.write("### 원 댓글들:")

        for _, content in st.session_state['comment_list'].iterrows():
                st.write(f"**작성자**: {content['parentComment']['author']}")
                st.write(f"**내용**: {content['parentComment']['text']}")
                if content['parentComment']['replies']:
                    st.write("**답글들:**")
                    for reply in content['parentComment']['replies']:
                        st.write(f"- **작성자**: {reply['author']}, **내용**: {reply['text']}")
                st.markdown("---")

    # 스팸 분류 버튼
    if st.session_state['show_classify_button']:
        if st.button("Classify Comments as Spam or Not Spam"):
            # 분류 로직 실행
            video_title = st.session_state['video_list'][0][1]
            classified_comments = get_classification_result(
                video_title, st.session_state['comment_list'], max_analysis=100
            )
            classified_df = pd.DataFrame(classified_comments)
            classified_df['comment_id'] = st.session_state['comment_list']['comment_id'].values
            st.session_state['classified_comments'] = classified_df

        # 스팸 댓글 표시
        if not st.session_state['classified_comments'].empty:
            st.write("### 스팸으로 분류된 댓글:")
            spam_comments = st.session_state['classified_comments'][
                st.session_state['classified_comments']['classification'] == 'Spam'
            ]
            if not spam_comments.empty:
                for _, row in spam_comments.iterrows():
                    st.write(f"**작성자**: {row['parentComment']['author']} / 댓글 내용: {row['parentComment']['text']}")
                    st.markdown("---")

                if st.button("Delete Classified Spam Comments"):
                    spam_comment_ids = spam_comments['comment_id'].tolist()
                    try:
                        youtube.comments().setModerationStatus(
                            id=spam_comment_ids,
                            moderationStatus='rejected',
                            banAuthor=False
                        ).execute()
                        st.success(f'{len(spam_comment_ids)}개의 스팸 댓글을 삭제했습니다.')
                    except googleapiclient.errors.HttpError as e:
                        st.error(f"Error deleting comments: {e}")
            else:
                st.write("스팸으로 분류된 댓글이 없습니다.")

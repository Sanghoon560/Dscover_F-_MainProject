import pandas as pd
DATAPATH =  "INPUT"
data = pd.read_csv(DATAPATH)
# Step 2: parent_id의 NaN 값 처리
data['parent_id'] = data['parent_id'].fillna('root')

# Step 3: structure_data 함수 정의
def structure_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    data를 구조화된 JSON 형태로 변환합니다.
    부모 댓글을 기준으로 각 행에 JSON 구조를 생성합니다.
    """
    rows = []

    video_title = data['video_title'].iloc[0]  # 비디오 제목 추가

    for parent_id, group in data.groupby('parent_id'):
        if parent_id == 'root':
            continue  # 최상위 댓글은 제외

        parent_comment_row = data[data['comment_id'] == parent_id]
        if not parent_comment_row.empty:
            parent_comment_text = parent_comment_row['text'].iloc[0]
            parent_author = parent_comment_row['author'].iloc[0]
            parent_have_spam = int(parent_comment_row['have_spam'].iloc[0])
        else:
            parent_comment_text = "[Deleted Comment]"
            parent_author = None
            parent_have_spam = 0

        replies = []
        replies_have_spam = 0

        for _, row in group[group['comment_id'] != parent_id].iterrows():
            replies.append({
                "text": row['text'],
                "author": row['author']
            })
            replies_have_spam = max(replies_have_spam, int(row['have_spam']))

        # 부모 댓글과 자식 댓글을 포함한 전체 have_spam 여부 계산
        set_have_spam = max(parent_have_spam, replies_have_spam)

        rows.append({
            "videoTitle": video_title,
            "parentComment": {
                "text": parent_comment_text,
                "author": parent_author,
                "replies": replies
            },
            "have_spam": set_have_spam
        })

    return pd.DataFrame(rows)

# Step 4: filter_unique_video_titles 함수 정의
def filter_unique_video_titles(df: pd.DataFrame) -> pd.DataFrame:
    """
    have_spam이 0인 항목 중 video_title이 동일한 것 하나씩만 남깁니다.
    """
    filtered_df = df[df['have_spam'] == 0]
    unique_titles = filtered_df.drop_duplicates(subset=['videoTitle'])
    return unique_titles

# Step 5: generate_structured_data 함수 정의
def generate_structured_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    주어진 DataFrame을 parent_id별로 그룹화하고 structure_data 함수를 적용하여 변환합니다.
    """
    result = structure_data(df)
    result = filter_unique_video_titles(result)
    return result

# Step 6: Groupby 및 결과 생성
structured_data = generate_structured_data(data)
print(json.dumps(structured_data.to_dict(orient="records"), indent=4, ensure_ascii=False))

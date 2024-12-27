import json
import google.generativeai as genai
import pandas as pd
from typing_extensions import TypedDict



class ClassificationResult(TypedDict):
    classification: str

# Initialize the Generative AI Model
model = genai.GenerativeModel("gemini-1.5-flash")
def get_instruction(video_title: str) -> str:
    """
    Generates a classification instruction for the provided video title using LLM.

    Args:
        video_title (str): The title of the video.

    Returns:
        str: A detailed classification instruction.
    """
    try:
        response = model.generate_content(
            f"""
            You are a content moderation assistant specialized in spam detection. Your task is to generate detailed instructions for detecting and filtering spam comments in YouTube videos.

            The video title is: "{video_title}".

            Consider the following while creating the instruction:
            1. What characteristics should be used to identify spam? Include:
            - Repetitive phrases, promotional links, offensive or deceptive language.
            - Suspicious or inappropriate usernames (e.g., excessive symbols, random patterns, or explicit language).
            - Comments irrelevant to the video's content.
            - Generic or impersonal tone suggesting automation.

            2. Should the author's name, comment structure, or reply context be taken into account?
            - Evaluate if the username shows signs of bot-like behavior or spam intent.
            - Consider if the comment structure aligns with natural human interaction.
            - Analyze if replies are coherent and relevant to the parent comment.

            3. How can spam comments be differentiated from genuine but critical or irrelevant comments?
            - Genuine critical comments are specific and contextual to the video.
            - Irrelevant but non-spam comments lack context but are not promotional, repetitive, or harmful.
            - Spam comments often include calls to action, promotional content, or irrelevant links.

            Provide the instruction in a clear and actionable format suitable for an AI or a manual reviewer to classify comments as either 'Spam' or 'Not Spam'.
            """,
            generation_config=genai.GenerationConfig(response_mime_type="text/plain")
        )
        print(response.text.strip())
        return response.text.strip()
    except Exception as e:
        print(f"Error generating instruction: {e}")
        return ""


def get_classification(comment_data: pd.DataFrame, instruction: str, max_analysis: int) -> pd.DataFrame:
    """
    Collects the top comments from the dataset, applies the classification instruction, 
    and returns the classification results in a DataFrame.

    Args:
        comment_data (pd.DataFrame): DataFrame containing comment data.
        instruction (str): Classification instruction for the comments.
        max_analysis (int): Number of top comments to analyze.

    Returns:
        pd.DataFrame: DataFrame with classification results.
    """
    comment_data = comment_data.head(max_analysis)
    classifications = []

    for _, row in comment_data.iterrows():
        try:
            comment = row.get('parentComment', "")
            if not comment:
                raise ValueError("Comment text is missing.")

            # Generate structured classification result
            response = model.generate_content(
                f"""
                You are a content moderation assistant. Your task is to classify the given comment set as either 'Spam' or 'Not Spam'.

                Spam comments include:
                1. Promotional content, irrelevant links, repetitive phrases, or any content that is deceptive, inappropriate, violates community guidelines, or includes explicit or offensive language.
                2. Comments written by authors with suspicious or inappropriate usernames. Consider the following:
                - Usernames containing excessive symbols, random characters, or patterns that suggest spam-like behavior.
                - Usernames with explicit, offensive, or promotional language.
                - Usernames suggesting automated or bot activity (e.g., repetitive or unnatural patterns).
                - Usernames resembling common numeric or alphabetic substitutions (e.g., 'l9' instead of '19', '1g' instead of 'lg').

                **Explicit and Inappropriate Language Detection**:
                - Identify comments containing explicit, vulgar, or sexual language that may be inappropriate or offensive.
                - Examples include words or phrases that are sexual, harassing, or excessively vulgar.
                - Analyze not only the text content but also indirect or coded language (e.g., common abbreviations or euphemisms for explicit terms).

                Not Spam comments are:
                1. Genuine, relevant, and contribute meaningfully to the discussion.
                2. Critical comments that are specific, contextual, and non-promotional.

                If even one comment in the set is Spam, classify the entire set as Spam.

                **Additional instructions**: {instruction}

                **Evaluation criteria**:
                1. Consider the author's username, the structure of the comment, and the context of any replies.
                2. Analyze if the comment set aligns with natural human interaction or exhibits spam-like patterns.
                3. Identify and flag explicit, vulgar, or inappropriate language as spam.

                **Comment set**:
                {comment}

                Provide the classification in JSON format, including the following:
                - `classification`: Either 'Spam' or 'Not Spam'.
                - `reason`: A brief explanation of why the classification was made.
                - `explicit_terms_detected`: A list of explicit or inappropriate terms detected in the comment (if any).
                """,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", response_schema=ClassificationResult,
                    temperature=0
                )
            )
            # Correctly extract JSON output from the first candidate
            if response.candidates:
                candidate_text = response.candidates[0].content.parts[0].text.strip()
                classifications.append(json.loads(candidate_text))
            else:
                classifications.append({"classification": "Error"})
        except Exception as e:
            print(f"Error processing comment: {row.get('parentComment', '')}. Error: {e}")
            classifications.append({"classification": "Error"})

    # Combine classifications with original data
    classification_df = comment_data.copy()
    classification_df["classification"] = [
        res.get("classification", "Error") for res in classifications
    ]
    return classification_df


def get_classification_result(video_title: str, comment_data: pd.DataFrame, max_analysis: int) -> dict:
    """
    Generates a final classification result for the video based on the comments.

    Args:
        video_title (str): The title of the video.
        comment_data (pd.DataFrame): DataFrame containing comment data.
        max_analysis (int): Number of top comments to analyze.

    Returns:
        dict: Final classification result in JSON format.
    """
    instruction = get_instruction(video_title)
    if not instruction:
        print("Instruction generation failed.")
        return []

    classification_df = get_classification(comment_data, instruction, max_analysis)
    return classification_df.to_dict(orient="records")




#주석 제거하면, 테스트로 실행가능. (max_analysis는 최대 분석할 댓글 수 이고, 우선 api 아끼기 위해 1로 설정)
# Test the functions 
# data = pd.read_csv('filtered_data.csv')
# video_title = data['videoTitle'].iloc[0]
# max_analysis = 1
# result = get_classification_result(video_title, data, max_analysis)
# print(json.dumps(result, indent=2, ensure_ascii=False))

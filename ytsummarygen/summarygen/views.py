from django.shortcuts import render
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import logging
import openai 
from django.conf import settings
from dotenv import load_dotenv
import os 

load_dotenv()  # Load environment variables from a .env file


def generate_summary(transcript):
    #openai.api_key = settings.OPENAI_API_KEY
    openai.api_key = os.getenv("OPEN_API_KEY")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": (
                    f"""
    Please summarize the following transcript in the specified format:

    Transcript:
    {transcript}

    Format:
    ### Summary
    Provide a brief overview of the main points discussed in the transcript. Don't specifiy its a trascript again. Just go with the summary. Speficy if the name of the speaker if you have that info. 

    ### Highlights
    Use bullet points with emojis to highlight the key points and important moments. Each point highlight by highlight emoji

    ### Key Insights
    Provide a detailed analysis of the main insights, including implications and importance of the discussed topics. Each point hightlighted by key emoji

    Now, provide the summary, highlights, and key insights in the specified format.
    """
                )
            }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content'].strip()
        else:
            return "No summary available."
    else:
        logging.error(f"Error in API response: {response.json()}")
        return "Error in API response."

def index(request):
    transcript_text = ""
    summary = ""
    
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        video_id = video_url.split('v=')[-1]

        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            print("Transcript probably generated")
            transcript_text = ' '.join([entry['text'] for entry in transcript])
            summary = generate_summary(transcript_text)
        except Exception as e:
            transcript_text = f"LOG: An error occurred: {e}"
    
    return render(request, 'summarygen/index.html', {'transcript_text': transcript_text, 'summary': summary})

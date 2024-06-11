from django.shortcuts import render
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import logging
import openai 
from django.conf import settings

def generate_summary(transcript):
    #openai.api_key = settings.OPENAI_API_KEY
    openai.api_key = `${{ OPEN_API_KEY }}`

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
                    f"Summarize the following transcript {transcript} in less than 1000 words in the following format:\n\n"
                    f"Summary:\n"
                    f"The transcript discusses the global concern revolving around employees being replaced by AI and the consequent need to learn and adapt to new skills. The speaker emphasises the necessity and benefits of reskilling programs in response to the rapid advancement of technology. Furthermore, the speaker highlights the remarkable efforts of the Singapore government's digital reskilling programs and implores individuals, companies, and governments to view these changes with curiosity and optimism.\n\n"
                    f"Highlights:\n"
                    f"🔹 AI and technology are significantly impacting jobs globally, with a third of workers likely to be affected this decade.\n"
                    f"🔹 The demand for talent in fields like data science, cybersecurity, and clean energy is growing but the skillset of employees become redundant in as little as five years, pointing out the short \"half life of skills\".\n"
                    f"🔹 Reskilling millions of people every year is the only effective solution to keep up with technology's rapid advancement.\n"
                    f"🔹 The Singapore government's proactive approach towards reskilling programs serves as a powerful example for other countries.\n"
                    f"🔹 The digital reskilling program \"Rise\" highlights the importance of not just technical skills but mindset and confidence.\n"
                    f"🔹 Companies play a critical role in the reskilling revolution, as illustrated by Ikea's reskilling initiative following the launch of their AI bot, Billy.\n"
                    f"🔹 Individuals have a personal responsibility to embrace lifelong learning and continually build their skills.\n\n"
                    f"Key Insights:\n"
                    f"🔑 The rapid advancement of technology requires individuals and companies to continually learn and adopt new skills.\n"
                    f"🔑 Reskilling programs are a critical response to the technology-induced job market changes.\n"
                    f"🔑 Apart from technical skills, reskilling initiatives should focus on building mindset and confidence.\n"
                    f"🔑 Companies and governments have a significant role in managing technology-induced changes in the workforce.\n"
                    f"🔑 Individuals have a personal responsibility to continually adopt new skills and maintain a lifelong learning approach."
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
            transcript_text = ' '.join([entry['text'] for entry in transcript])
            summary = generate_summary(transcript_text)
        except Exception as e:
            transcript_text = f"An error occurred: {e}"
    
    return render(request, 'summarygen/index.html', {'transcript_text': transcript_text, 'summary': summary})

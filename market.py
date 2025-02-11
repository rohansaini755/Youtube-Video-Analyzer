import yt_dlp
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
import assemblyai as aai
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


def analyze_the_market(result_text, query):
    result_text = "query is : " + query + " and result is : " + result_text + " above information is the research of some market analyst about the unlisted share in indian stock market. analyse all the stratement and make a common conclusion. tell me the estimate date of listing of these share. estimate listing price, how much strong the share is. market interest, how strong fundamentals is. all necessary inormation about that share, beacuase i want to invest. and according to these statements, in which sahre should i invest? Also some analysis by your self."
    genai.configure(api_key="AIzaSyDjSFPcvYsJP4dBXIcTYdxaWpb9n8YCUWc")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(result_text)
    print("\n Analysis of market is : \n")
    print(response.text)


def transcribe_with_assemblyai(audio_file):

    aai.settings.api_key = "bead54e569574ae4a725b253315f8553"
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(audio_file)
    # transcript = transcriber.transcribe("./my-local-audio-file.wav")
    print(transcript.text)
    return transcript.text


def download_audio(video_url, video_id, output_path='downloads', cookies_file='www.youtube.com_cookies.txt'):
    try:
        print(f"Downloading audio for video: {video_id}")

        # Ensure the output path exists
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/{video_id}.%(ext)s',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }
            ],
            'cookiefile': cookies_file if os.path.exists(cookies_file) else None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=True)
            mp3_file_path = f"{output_path}/{video_id}.mp3"
            return mp3_file_path if os.path.exists(mp3_file_path) else None

    except Exception as e:
        print(f"An error occurred during download for video {video_id}: {e}")
        return None




def process_video(video):
    video_url = video['url']
    video_id = video['id']
    title = video['title']
    channel = video['channel']
    published_date = video['published_date']

    # Define the path where the MP3 should be saved
    downloads_dir = "downloads"
    mp3_file_path = os.path.join(downloads_dir, f"{video_id}.mp3")

    # Create the downloads directory if it doesn't exist
    os.makedirs(downloads_dir, exist_ok=True)

    # Check if the file already exists
    if not os.path.isfile(mp3_file_path):
        print(f"Downloading audio for video ID: {video_id}")
        downloaded_path = download_audio(video_url, video_id)
        if not downloaded_path:
            # Handle download failure
            return {
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "published_date": published_date,
                "transcription": "Failed to download audio."
            }
    else:
        print(f"Audio for video ID {video_id} already exists. Skipping download.")
        downloaded_path = mp3_file_path

    # Proceed with transcription
    if downloaded_path:
        print("\ntranscription of audio has been started.")
        transcription = transcribe_with_assemblyai(downloaded_path)
        return {
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "published_date": published_date,
            "transcription": transcription
        }
    else:
        return {
            "video_id": video_id,
            "title": title,
            "channel": channel,
            "published_date": published_date,
            "transcription": "Failed to process audio."
        }






def fetch_youtube_video_details(query, api_key):
    """
    Process sub-queries in parallel using multithreading.
    """
    transcriptions = []
    result_text = ""
    current_time = datetime.now(pytz.UTC)
    one_week_ago = current_time - timedelta(days=1)

    try:
        # Split queries and create YouTube client
        sub_queries = [q.strip() for q in query.split("OR") if q.strip()]
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Process sub-queries in parallel
        with ThreadPoolExecutor(max_workers=4) as query_executor:
            # Create futures for each sub-query
            futures = {
                query_executor.submit(
                    process_sub_query,
                    sub_q,
                    youtube,
                    one_week_ago
                ): sub_q for sub_q in sub_queries
            }

            # Collect results as they complete
            for future in as_completed(futures):
                sub_result = future.result()
                transcriptions.extend(sub_result)
                print(f"Completed processing for: {futures[future]}")

        # Combine all results
        for transcription in transcriptions:
            result_text += (
                f"text_name: {transcription['title']} "
                f"text_provider_name: {transcription['channel']} "
                f"text_content: {transcription['transcription']}\n"
            )

        analyze_the_market(result_text, query)

    except Exception as e:
        print(f"Top-level error: {e}")



def process_sub_query(sub_query, youtube, one_week_ago):

    try:
        print(f"Starting sub-query: {sub_query}")
        request = youtube.search().list(
            part="snippet",
            q=sub_query,
            type="video",
            maxResults=3
        )
        response = request.execute()

        videos = []
        for item in response['items']:
            video_id = item['id']['videoId']
            published_at = item['snippet']['publishedAt']
            published_at_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

            if published_at_dt < one_week_ago:
                continue

            videos.append({
                "id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "title": item['snippet']['title'],
                "channel": item['snippet']['channelTitle'],
                "published_date": published_at
            })

        # Process videos in parallel for this sub-query
        sub_transcriptions = []
        if videos:
            with ThreadPoolExecutor(max_workers=12) as video_executor:
                results = list(video_executor.map(process_video, videos))
            sub_transcriptions.extend(results)

        return sub_transcriptions

    except Exception as e:
        print(f"Error in sub-query '{sub_query}': {e}")
        return []


# Replace with your API Key and search query

# Impact of global markets on Indian stocks 30 january 2025
# OR Impact of global markets on Indian stocks 30 january 2025
# OR Indian stock market fundamentals and short-term outlook 30 january 2025
# OR Nifty 50 technical analysis for 30 january 2025 trading session
# OR Bank Nifty support and resistance levels for 30 january 2025
# OR Sensex Nifty prediction for 30 january 2025 by experts
# OR Today's Indian stock market live updates and 30 january 2025's trend
# OR Stock market news today and 30 january 2025's trading strategy
# OR Impact of [current event, e.g., RBI policy, elections] on Indian stock market 30 january 2025
# OR Indian stock market chart patterns and 30 january 2025's levels
# OR Technical analysis of Nifty 50 and Bank Nifty for 30 january 2025
# OR Market closing bell analysis and 30 january 2025 predictions
# OR Daily Indian stock market wrap-up and 30 january 2025's outlook
# OR Intraday trading tips for Indian market 30 january 2025
# OR 30 january 2025's Nifty 50 and Sensex forecast
# OR Indian stock market prediction for 30 january 2025
# OR 29 january 2025 market conditions India expert opinion
# OR Latest Indian stock market updates and trends
# OR 30 january 2025's Indian stock market analysis Nifty 50 Sensex
# Indian stock market prediction for 30 january 2025
# OR 29 january 2025 market conditions India expert opinion
# Tata Motors share price analysis
# OR Tata Motors share price prediction"
# OR Tata Motors share price target"
# OR Tata Motors share price technical analysis"
# OR Tata Motors share price outlook"
# OR Is it a good time to buy Tata Motors shares?
# OR What is the future of Tata Motors share price?
# OR Tata Motors share price analysis for beginners
# OR Tata Motors share price analysis in Hindi
# India Budget 2025 Expectations
# OR Expert Opinion on Budget 2025
# OR Budget 2025 Impact on Electric Vehicle Stocks
# OR Budget 2025 and Olectra Greentech
# OR Olectra Greentech Share Price Prediction 31st January 2025
API_KEY = "AIzaSyC24qvy6xEeyjZQ7FYZGzeptLFsSbZCs4Q"  # Replace with a valid YouTube Data API key
SEARCH_QUERY = """Upcoming IPOs in India 2025
OR OYO pre-IPO Analysis
OR OYO IPO Date and Price
OR OYO Fundamental Analysis
OR studd pre-ipo analysis
OR studd IPO date and price
OR studd fundamental analysis
OR Bira pre-ipo analysis
OR Bira ipo date and price
OR Bira fundamental analysis
OR tata capital pre-ipo analysis
OR tata capital date and price
OR tata capital fundamental analysis
"""

fetch_youtube_video_details(SEARCH_QUERY, API_KEY)
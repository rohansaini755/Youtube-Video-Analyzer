# Youtube-Video-Analyzer
This program analyze the particular stock related youtube video, convert that audio file into text and than analyze the data using AI and make a common conclusion.

Problem Faced : 
1 - Youtube Api related - need to add latest youtube cookies file. Also youtube search api can give only maxium 50 result at a time.
2 - AssemblyAi related - It has a limit to convert audio to text, after the limit the process get slow in free tier.

Installation of library and packages :-
1 -pip install yt-dlp
2 - pip install ffmpeg-python
3 - pip install google-api-python-client
4 - pip install assemblyai

How to Run :-
Before run add the necessary api key and youtube cookies file in current working directory.
And than just run the python program.

Code Description :-
1 : Code start with splitting the the queries into sub queries and than further process start with all sub queries seperatly using multthreading.
2 : For each sub queries, a list of youtube video with youtube video Id is get using youtube search api and append the all detail in a list "videos".
3 : And for each video, a different multithreading enviroment run, in which every single video is processed.
4 : During the process of video, a audio file is downloaded with the help of yt_dlp youtube api and saved into the folder with the name video_id.mp3. But before downloading of every video, it always check that 
    it is present in the download directory or not.
5 : After Downloading part, the downloaded video path is sent to the next step of converting audio to text using AssemblyAI api.
6 : As the transcription part is done, the transcribe text is stored in an array, and in last step by adding some more detail to the transcribe text the data is sent to the Gemini for the analysis.

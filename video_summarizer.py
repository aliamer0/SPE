import cv2
from moviepy.editor import *
import librosa
import numpy as np
import tempfile
import mysql.connector
from datetime import date, datetime, timedelta
import os
import torch
from torchvision import models, transforms
from PIL import Image
import subprocess
from deep_sort_realtime.deepsort_tracker import DeepSort
from tqdm import tqdm
import whisper
from pysrt import SubRipFile, SubRipItem


# Database connection
conn = mysql.connector.connect(host="localhost",
                               user="ali",
                               password="456430",
                               database="movies01")

cursor = conn.cursor()
start_date = date(2024, 12, 5)
end_date = date(2024, 12, 10)
sql_query = f"SELECT id, title, release_date, rating, plot FROM movies WHERE MONTH(release_date) = {start_date.month} AND DAY(release_date) = {start_date.day} ORDER BY number_of_ratings DESC, rating DESC limit 10;"
cursor.execute(sql_query)
rows = cursor.fetchall()
j = 1

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.mobilenet_v3_large(pretrained=True)
model.eval().to(device)

# Transform for video frames
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def transcribe_audio(video_clip):
    # Extract audio from MoviePy video object
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        audio_path = temp_audio_file.name
        video_clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
    
    # Load Whisper model and transcribe
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    captions = []
    for segment in result['segments']:
        for word_info in segment['words']:
            start = word_info['start']
            end = word_info['end']
            text = word_info.get('word', '')  # Safely get the 'word' key
            captions.append((start, end, text))
    
    return captions

# Step 2: Save captions as SRT
def time_to_srt_timestamp(seconds):
    """Converts seconds into SRT timestamp format (HH:MM:SS,MS)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

def save_as_srt(captions, srt_path):
    srt_file = SubRipFile()
    for i, (start, end, text) in enumerate(captions):
        srt_file.append(
            SubRipItem(
                index=i+1,
                start=time_to_srt_timestamp(start),
                end=time_to_srt_timestamp(end),
                text=text.strip()
            )
        )
    srt_file.save(srt_path, encoding='utf-8')

# Step 3: Burn captions into the video
def burn_captions_to_video(video, captions, output_path):
    text_clips = []
    for start, end, text in captions:
        txt_clip = TextClip(
            text,
            fontsize=100,
            color='yellow',  # Yellow text color
            font='LiberationSans-Bold',  # Use a system font that's more likely to be available
        ).set_position(("center", "center")).set_start(start).set_duration(end - start)
        text_clips.append(txt_clip)
    final_video = CompositeVideoClip([video] + text_clips)
    return final_video





##def enhance_video(input_path, output_path):
##    """
##    Enhance video quality using a combination of Real-ESRGAN and FFmpeg filters.
##    """
##    # Temporary upscale with Real-ESRGAN
##    temp_upscaled_path = input_path.replace(".mp4", "_upscaled.mp4")
##    subprocess.run(f"realesrgan-ncnn-vulkan -i {input_path} -o {temp_upscaled_path} -s 2", shell=True)
##
##    # Apply FFmpeg post-processing for denoising, sharpening, and color grading
##    filters = "hqdn3d=1.5:1.5:6:6,eq=contrast=1.2:brightness=0.05:saturation=1.3,unsharp"
##    subprocess.run(f"ffmpeg -i {temp_upscaled_path} -vf \"{filters}\" -c:v h264_nvenc -preset fast -b:v 5M {output_path}", shell=True)
##
##    # Cleanup temporary file
##    os.remove(temp_upscaled_path)



# Analyze frames using PyTorch model
def analyze_frames_batch(frames):
    # Convert each frame to PIL Image and apply transformations
    batch_tensors = []
    for frame in frames:
        pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        batch_tensors.append(transform(pil_frame))
    
    # Stack all frames into a single batch tensor
    input_tensor = torch.stack(batch_tensors).to(device)
    
    # Get model predictions in batch
    with torch.no_grad():
        outputs = model(input_tensor)
    
    # Return confidence scores for each frame
    return torch.max(outputs, 1)[0].cpu().numpy()

# Emotion detection for smarter scene selection
def detect_emotion(frame):
    # Placeholder function for emotion detection
    # This should use a model like FER2013 or OpenCV's pre-trained models for emotion recognition
    emotion = "happy"  # Example, should be dynamically detected based on the frame
    return emotion


def is_static_frame(frame, prev_frame, motion_threshold=10.0):
    # Convert frames to grayscale for motion detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(prev_frame, gray)
    motion_value = np.mean(diff)
    return motion_value < motion_threshold  # Flag as static if motion is below the threshold


# Scene detection with motion, emotion, and PyTorch analysis
# Updated scene detection with improved motion threshold and fallback strategies
def detect_scenes_with_motion(video_path, initial_threshold=60.0, max_duration=30, min_duration=0, batch_size=256):
    cap = cv2.VideoCapture(video_path)
    scenes = []
    prev_frame = None
    frame_count = 0
    start = 0
    scene_scores = []
    frame_buffer = []  # Buffer to hold frames for batch processing
    motion_values = []  # Store motion differences to calculate dynamic threshold

    # Pre-scan the video to calculate average motion intensity
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray)
            motion_values.append(np.mean(diff))

        prev_frame = gray

    cap.release()

    # Calculate the dynamic threshold based on motion values
    if motion_values:
        avg_motion = np.mean(motion_values)
        std_motion = np.std(motion_values)
        threshold = avg_motion + (0.5 * std_motion)
        threshold = max(threshold, 20)  # Ensure a minimum threshold
    else:
        threshold = initial_threshold  # Default fallback

    print(f"Dynamic threshold set to: {threshold}")

    # Re-open the video for actual scene detection
    cap = cv2.VideoCapture(video_path)
    prev_frame = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None and is_static_frame(frame, prev_frame):
            frame_count += 1
            continue  # Skip static frames

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray)
            diff_mean = np.mean(diff)
            if diff_mean > threshold:
                end = frame_count / cap.get(cv2.CAP_PROP_FPS)
                if min_duration <= (end - start) <= max_duration:
                    # Calculate average score from the accumulated batch scores
                    avg_score = np.mean(scene_scores) if scene_scores else 0
                    scenes.append((start, end, avg_score))
                start = end
                scene_scores = []

            frame_buffer.append(frame)  # Add frame to buffer

            # If buffer is full, process frames in batch
            if len(frame_buffer) >= batch_size:
                batch_scores = analyze_frames_batch(frame_buffer)
                scene_scores.extend(batch_scores)
                frame_buffer = []  # Clear buffer after processing

        prev_frame = gray
        frame_count += 1

    # Process remaining frames in the buffer
    if frame_buffer:
        batch_scores = analyze_frames_batch(frame_buffer)
        scene_scores.extend(batch_scores)

    cap.release()

    # Fallback: Random sampling if no scenes detected
    if not scenes:
        print("No scenes detected using motion. Applying fallback random sampling.")
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        for _ in range(3):  # Pick 3 random scenes as fallback
            start_frame = np.random.randint(0, total_frames - int(fps * 5))
            start_time = start_frame / fps
            end_time = min(start_time + 5, total_frames / fps)
            scenes.append((start_time, end_time, 0))  # Zero score for fallback scenes

    return scenes

# Analyze audio features
def analyze_audio_features(clip, start, end):

        
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        temp_audio_file_name = temp_audio_file.name
        clip.audio.write_audiofile(temp_audio_file_name, codec="aac")
        audio_data, sr = librosa.load(temp_audio_file_name, sr=None)
        rms = librosa.feature.rms(y=audio_data).mean()
        
    os.remove(temp_audio_file_name)  # Clean up the temporary file
    return rms



# Find engaging scenes with additional factors like emotion and object detection
def find_engaging_scenes(video_path, max_duration=30, plot_text=""):
    scenes = detect_scenes_with_motion(video_path)
    scenes_with_engagement = []
    keywords = ["love", "fight", "escape", "revenge", "mystery", "hero", "villain", "sacrifice", "adventure"]
    matching_score = sum(1 for word in keywords if word in plot_text.lower())

    for start, end, scene_score in scenes:
        segment_start = start
        while segment_start < end:
            # Determine segment duration (5 seconds or remaining duration of the scene)
            segment_end = min(segment_start + 5, end)
            if segment_end - segment_start <= 0.01:
                segment_start += 5
                continue
            fullclip = VideoFileClip(video_path)
            print("actual length: ", fullclip.duration)
            clip = fullclip.subclip(segment_start, segment_end)
            print("start: ", segment_start, "     end: ", segment_end)
            audio_intensity = analyze_audio_features(clip, segment_start, segment_end)
            
            # Emotion-based engagement score (happy moments get higher scores)
            emotion = detect_emotion(video_path)
            if emotion == "happy":
                engagement_score = (0.6 * audio_intensity) + (0.3 * scene_score) + (0.1 * matching_score)
            elif emotion == "angry":
                engagement_score = (0.5 * audio_intensity) + (0.4 * scene_score) + (0.1 * matching_score)
            else:
                engagement_score = (0.5 * audio_intensity) + (0.4 * scene_score) + (0.2 * matching_score)

            scenes_with_engagement.append((engagement_score, segment_start, segment_end))
            segment_start += 5  # Move to the next segment

    # Sort segments by engagement score in descending order
    scenes_with_engagement.sort(reverse=True, key=lambda x: x[0])

    selected_scenes = []
    total_duration = 0

    for _, start, end in scenes_with_engagement:
        duration = end - start
        if total_duration + duration <= max_duration:
            selected_scenes.append((start, end))
            total_duration += duration
        if total_duration >= max_duration:
            break

    # Sort selected scenes by their start time to ensure chronological order
    return sorted(selected_scenes, key=lambda x: x[0])

clip_list = []


# Extract and combine clips with adaptive transitions and dynamic text overlays
def extract_and_combine_clips(video_path, output_path, output_path1, cap_path, scenes, transition_duration=0.25):
    clips = []
    for start, end in scenes:
        clip = VideoFileClip(video_path).subclip(start, end).resize((1080, 1920))
        clips.append(clip)

    # Adaptive transitions based on audio intensity
    for i in range(1, len(clips) - 1):
        if clips[i].audio is not None:  # Check if the clip has audio
            try:
                audio_intensity = clips[i].audio.to_soundarray(fps=22050).mean()
            except Exception as e:
                print(f"Error processing audio in clip: {e}")
                audio_intensity = 0.05  # Default value if audio processing fails
        else:
            audio_intensity = 0.05  # Default intensity if no audio is present

        adaptive_transition = max(transition_duration * (audio_intensity / 0.05), 0.15)
        clips[i] = clips[i].crossfadeout(adaptive_transition)
        clips[i + 1] = clips[i + 1].crossfadein(adaptive_transition)

    # Add movie poster and text clip
    image_clip = ImageClip(f"5105.jpg", duration=2).fadein(0.5).fadeout(0.5).resize((1080, 1920))
    text_clip = TextClip(f"\n Release date: \n Rating: ", fontsize=60, color="white", font="Arial", size=(1080, 1920)).set_position("center", "center").set_duration(2).fadein(0.5).fadeout(0.2)
    image_with_text = CompositeVideoClip([image_clip, text_clip])
    clips.append(image_with_text)

    # Combine all clips
    final_clip = concatenate_videoclips(clips, method="chain").resize((1080, 1920))
    # Generate subtitles
    video_audio = final_clip.audio
    final_audio = CompositeAudioClip([video_audio]).set_fps(44100)  # Set FPS explicitly
    final_clip = final_clip.set_audio(final_audio)
    captions = transcribe_audio(final_clip)
    save_as_srt(captions, cap_path)
    text_clips = []
    for start, end, text in captions:
        txt_clip = TextClip(
            text,
            fontsize=100,
            color='yellow',  # Yellow text color
            font='LiberationSans-Bold',  # Use a system font that's more likely to be available
        ).set_position(("center", "center")).set_start(start).set_duration(end - start)
        text_clips.append(txt_clip)
##        txt_clip.close()
    final_video = CompositeVideoClip([final_clip] + text_clips)
    final_video.write_videofile(output_path1, threads = 12)
    # Free up resources
    for clip in clips:
        clip.close()
    for clip in text_clips:
        clip.close()
    final_clip.close()
    final_video.close()



### Main loop
##
##    
##video_path = f"5105.mp4"
##output_path = f"output.mp4"
##output_path1 = f"output2.mp4"
##cap_path = f"captions.srt"
##output_dir = os.path.dirname(output_path)
##os.makedirs(output_dir, exist_ok=True)
##output_dir1 = os.path.dirname(output_path1)
##os.makedirs(output_dir1, exist_ok=True)
####        with open (f"output/{row[2].month}-{row[2].day}/#{i}-{row[0]}-script.txt", "r") as file:
####            script = file.read()
##
####        script = script.strip()
##
##plot_text = ""
##scenes = find_engaging_scenes(video_path, max_duration=20, plot_text=plot_text)
##if scenes:
##    extract_and_combine_clips(video_path, output_path, output_path1, cap_path, scenes)
##else:
##    print(f"No suitable scenes found for clipping in {video_path}.")
##
### Close the database connection
##conn.close()

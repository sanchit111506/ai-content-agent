import os
import re
import requests
import textwrap

from dotenv import load_dotenv

from gtts import gTTS

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx
)

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

os.makedirs("generated_videos", exist_ok=True)


# -----------------------------------
# CLEAN SCRIPT
# -----------------------------------
def clean_script(script):

    script = re.sub(r'#', '', script)
    script = re.sub(r'\*', '', script)
    script = re.sub(r'-', '', script)
    script = re.sub(r'\n+', '\n', script)

    return script.strip()


# -----------------------------------
# SPLIT INTO SCENES
# -----------------------------------
def split_into_scenes(script):

    scenes = script.split(".")

    return [
        scene.strip()
        for scene in scenes
        if len(scene.strip()) > 25
    ]


# -----------------------------------
# DOWNLOAD STOCK VIDEO
# -----------------------------------
def download_stock_video(query, output_path):

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    url = (
        f"https://api.pexels.com/videos/search"
        f"?query={query}&per_page=1"
    )

    response = requests.get(
        url,
        headers=headers
    )

    data = response.json()

    if not data.get("videos"):
        return None

    try:

        video_url = (
            data["videos"][0]
            ["video_files"][0]
            ["link"]
        )

    except Exception:
        return None

    video_data = requests.get(video_url)

    with open(output_path, "wb") as f:
        f.write(video_data.content)

    return output_path


# -----------------------------------
# GENERATE VIDEO
# -----------------------------------
def generate_video(
    script,
    output_name="final_video.mp4"
):

    print("Cleaning script...")

    cleaned_script = clean_script(script)

    print("Splitting into scenes...")

    scenes = split_into_scenes(
        cleaned_script
    )

    final_clips = []

    for index, scene in enumerate(scenes):

        try:

            print(f"Generating scene {index + 1}")

            # -----------------------------------
            # Generate narration
            # -----------------------------------
            tts = gTTS(
                text=scene,
                lang="en"
            )

            audio_path = (
                f"generated_videos/audio_{index}.mp3"
            )

            tts.save(audio_path)

            audio_clip = AudioFileClip(
                audio_path
            )

            duration = audio_clip.duration

            # -----------------------------------
            # Download stock footage
            # -----------------------------------
            video_path = (
                f"generated_videos/scene_{index}.mp4"
            )

            downloaded = download_stock_video(
                scene.split()[0],
                video_path
            )

            if not downloaded:

                print(f"No stock footage found for scene {index + 1}")

                continue

            # -----------------------------------
            # Load stock footage
            # -----------------------------------
            video_clip = VideoFileClip(
                video_path
            )

            # -----------------------------------
            # Loop video if shorter than audio
            # -----------------------------------
            if video_clip.duration < duration:

                video_clip = video_clip.with_effects([
                    vfx.Loop(duration=duration)
                ])

            # -----------------------------------
            # Trim exact duration
            # -----------------------------------
            video_clip = (
                video_clip
                .subclipped(0, duration)
                .with_audio(audio_clip)
            )

            # -----------------------------------
            # Create subtitles
            # -----------------------------------
            subtitle = TextClip(
                text=textwrap.fill(scene, 40),
                font_size=40,
                color="white",
                size=(1100, None),
                method="caption"
            ).with_duration(duration)

            subtitle = subtitle.with_position(
                ("center", "bottom")
            )

            # -----------------------------------
            # Combine video + subtitles
            # -----------------------------------
            final_scene = CompositeVideoClip([
                video_clip,
                subtitle
            ])

            final_scene = final_scene.with_duration(
                duration
            )

            final_clips.append(final_scene)

        except Exception as e:

            print(f"Scene {index + 1} failed: {e}")

            continue

    # -----------------------------------
    # Ensure clips exist
    # -----------------------------------
    if not final_clips:

        raise Exception(
            "No video scenes were generated."
        )

    print("Combining scenes...")

    # -----------------------------------
    # Merge all scenes
    # -----------------------------------
    final_video = concatenate_videoclips(
        final_clips,
        method="compose"
    )

    output_path = (
        f"generated_videos/{output_name}"
    )

    print("Rendering final video...")

    # -----------------------------------
    # Export final MP4
    # -----------------------------------
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    print("Video generation completed!")

    return output_path
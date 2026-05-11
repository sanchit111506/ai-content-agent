from memory.memory_manager import (
    save_interaction,
    get_recent_memory
)

import os
from datetime import datetime

from crewai import Task, Crew

from agents.writer_agent import writer_agent
from agents.seo_agent import seo_agent
from agents.research_agent import research_agent
from agents.video_agent import video_agent

from video_pipeline.video_generator import generate_video


def generate_content(prompt):

    # Load recent conversation memory
    recent_memory = get_recent_memory()

    # Create timestamp early for reuse
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Detect if SEO is requested
    seo_keywords = [
        "seo",
        "seo optimized",
        "seo friendly",
        "blog",
        "rank on google",
        "search engine optimization",
        "keyword optimization"
    ]

    seo_requested = any(
        keyword in prompt.lower()
        for keyword in seo_keywords
    )

    # Detect if Video creation is requested
    video_keywords = [
        "video",
        "youtube",
        "youtube video",
        "shorts",
        "reel",
        "create video",
        "video script",
        "cinematic"
    ]

    video_requested = any(
        keyword in prompt.lower()
        for keyword in video_keywords
    )

    # Research Task
    research_task = Task(
        description=f"""
        Recent Conversation Context:
        {recent_memory}

        Research detailed and latest information about:
        {prompt}

        Use:
        - internet search
        - uploaded PDFs
        - local knowledge base

        Requirements:
        - Collect accurate information
        - Include important concepts
        - Include real-world examples
        - Combine internet and document knowledge
        - Make research detailed and informative
        """,

        expected_output="Detailed research information",

        agent=research_agent
    )

    # Writing Task
    writing_task = Task(
        description=f"""
        Recent Conversation Context:
        {recent_memory}

        Write a detailed high-quality article
        about:
        {prompt}

        Requirements:
        - Create sections dynamically based on the topic
        - Add examples where relevant
        - Make the content engaging and informative
        - Add a strong conclusion
        """,

        expected_output="Complete article",

        agent=writer_agent
    )

    # SEO Task
    seo_task = Task(
        description=f"""
        Recent Conversation Context:
        {recent_memory}

        Optimize the following article for:
        - SEO
        - readability
        - engagement
        - keyword optimization
        - proper formatting

        Topic:
        {prompt}
        """,

        expected_output="SEO optimized article",

        agent=seo_agent
    )

    # Video Task
    video_task = Task(
        description=f"""
        Recent Conversation Context:
        {recent_memory}

        Create a professional video script about:
        {prompt}

        Requirements:
        - Create engaging intro hook
        - Add scene-by-scene breakdown
        - Include narration
        - Add visual suggestions
        - Create YouTube-style storytelling
        - Add strong ending CTA
        """,

        expected_output="Complete video production script",

        agent=video_agent
    )

    # Dynamic task list
    tasks = [
        research_task,
        writing_task
    ]

    # Add SEO task only if requested
    if seo_requested:
        tasks.append(seo_task)

    # Add Video task only if requested
    if video_requested:
        tasks.append(video_task)

    # Dynamic agent list
    agents = [
        research_agent,
        writer_agent
    ]

    # Add SEO agent only if needed
    if seo_requested:
        agents.append(seo_agent)

    # Add Video agent only if needed
    if video_requested:
        agents.append(video_agent)

    # Create Crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True
    )

    # Run CrewAI pipeline
    result = crew.kickoff()

    # Create output folders
    os.makedirs("generated_content", exist_ok=True)
    os.makedirs("generated_videos", exist_ok=True)

    # Save generated content
    filename = f"generated_content/content_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(str(result))

    print(f"Content saved successfully: {filename}")

    # Generate video automatically if requested
    if video_requested:

        try:

            print("Starting AI video generation pipeline...")

            video_file = generate_video(
                str(result),
                output_name=f"video_{timestamp}.mp4"
            )

            print(f"Video generated successfully: {video_file}")

        except Exception as e:

            print(f"Video generation failed: {e}")

    # Save conversation memory to PostgreSQL
    save_interaction(prompt, result)

    print("Conversation memory saved successfully!")

    return result
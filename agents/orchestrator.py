from crewai import Task, Crew

from agents.writer_agent import writer_agent
from agents.seo_agent import seo_agent
from agents.research_agent import research_agent


def generate_content(prompt):

    research_task = Task(
        description=f"""
        Research the following topic thoroughly:
        {prompt}
        """,
        expected_output="Detailed research summary",
        agent=research_agent
    )

    writing_task = Task(
        description=f"""
        Write a detailed high-quality SEO friendly article
        about:
        {prompt}

        Include:
        - introduction
        - technical explanation
        - examples
        - conclusion
        """,
        expected_output="Complete article",
        agent=writer_agent
    )

    seo_task = Task(
        description="""
        Optimize the article for:
        - SEO
        - readability
        - engagement
        - keyword optimization
        - proper formatting
        """,
        expected_output="SEO optimized article",
        agent=seo_agent
    )

    crew = Crew(
        agents=[
            research_agent,
            writer_agent,
            seo_agent
        ],
        tasks=[
            research_task,
            writing_task,
            seo_task
        ],
        verbose=True
    )

    result = crew.kickoff()

    return result
import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"


def _get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_source(topic: str, text: str) -> str:
    """
    Ask Groq to summarize one source in the context of the research topic.
    Returns a 3-5 sentence summary string.
    """
    prompt = f"""You are a research assistant.
Given the following web page content about "{topic}", write a concise 3-5 sentence summary
of the most relevant and important information.

Web page content:
{text}

Summary:"""

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate_report(topic: str, summaries: list[dict]) -> str:
    """
    Ask Groq to generate a full structured research report from all source summaries.
    Returns a markdown-formatted report string.
    """
    summaries_text = "\n\n".join(
        f"Source {i+1} ({s['url']}):\n{s['summary']}"
        for i, s in enumerate(summaries)
    )

    prompt = f"""You are an expert research analyst.
Based on the following source summaries about "{topic}", write a comprehensive,
well-structured research report in Markdown format.

Include:
- An introduction explaining the topic
- Key findings and insights from the sources
- A conclusion summarizing the main takeaways

Source summaries:
{summaries_text}

Research Report (in Markdown):"""

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

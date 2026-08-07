from openai import OpenAI
import json


class ChatSession:
    def __init__(self, system_prompt, model="gemma4:26b-a4b-it-q4_K_M"):
        self.model = model
        self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        self.messages = [{"role": "system", "content": system_prompt}]

    def get_response(self, user_content: str) -> str:
        self.messages.append({"role": "user", "content": user_content})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.1,          # more deterministic

        )
        answer = response.choices[0].message.content

        return answer


def resume_matcher(job: dict[str, list[str]]):

    candidate = {
        "name": "Iman Rezaeian",
        "title": "Software Engineer",
        "years": 15,
        "python_backend_years": 5,
        "core": ["FastAPI", "Django", "Flask", "System Architecture", "Design Patterns", "Financial Algorithms"],
        "impact": [
            "legacy processing 24h → 26min",
            "data collection 10min → <30s"
        ],
        "stack": ["Python", "FastAPI", "Golang", "Pandas", "PostgreSQL", "Docker", "Git"],
        "domains": ["Multi-tenant", "Financial systems", "Trading strategies"],
        "education": "B.S. Software Engineering",
        "strengths": ["Optimization", "Problem-solving", "Team player"]
    }

    system = """You are a strict technical recruiter.
Input is JSON: {"candidate": {...}, "job": {...}}.
Reply ONLY with valid JSON in this exact schema:
{
  "match_percent": <0-100 integer>,
  "strengths": ["...", "...", "..."],
  "gaps": ["...", "...", "..."],
  "recommendations": ["...", "...", "..."]
}
No markdown, no extra text."""

    payload = {"candidate": candidate, "job": job}
    user_msg = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))  # minimal whitespace

    chat = ChatSession(system, model="gemma4:latest")
    response = chat.get_response(user_msg)
    print(response)
    return response

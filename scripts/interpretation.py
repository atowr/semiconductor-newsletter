import json
import os
import requests

from validator import validate_interpretation


def interpret_article(article):
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    prompt = f"""
Interpret this semiconductor industry article.
Use only facts supplied below. Do not invent details.
Return JSON with exactly these fields:
what_happened, why_it_matters, adviser_relevance,
client_impact, market_significance.
what_happened: 25-40 words.
why_it_matters: 20-30 words.

Title: {article['title']}
Source: {article['source']}
Summary: {article.get('summary', '')}
URL: {article['url']}
"""

    response = requests.post(
        os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        .rstrip("/") + "/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "messages": [
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = json.loads(response.json()["choices"][0]["message"]["content"])

    for _ in range(3):
        if validate_interpretation(data):
            return data
        prompt += "\nVALIDATION ERROR: Correct the required five string fields and word counts. Return corrected JSON only."
        response = requests.post(
            os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                  "messages": [{"role": "system", "content": "Return valid JSON only."},
                               {"role": "user", "content": prompt}],
                  "temperature": 0, "response_format": {"type": "json_object"}},
            timeout=120,
        )
        response.raise_for_status()
        data = json.loads(response.json()["choices"][0]["message"]["content"])
    raise ValueError("DeepSeek response failed validation after 3 attempts")

import os
import json


def _chat(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    model = os.getenv("OPENAI_MODEL", "gpt-5")
    try:
        import openai  # type: ignore
        client = openai.OpenAI(api_key=api_key) if hasattr(openai, "OpenAI") else None
        if client:
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a top-tier Etsy SEO copywriter. Reply with compact JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            return r.choices[0].message.content if r.choices else None
        else:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a top-tier Etsy SEO copywriter. Reply with compact JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
            )
            return completion["choices"][0]["message"]["content"]
    except Exception:
        pass
    try:
        import requests
        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a top-tier Etsy SEO copywriter. Reply with compact JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
        }
        r = requests.post(url, headers=headers, json=body, timeout=60)
        if r.status_code >= 400:
            return None
        j = r.json()
        return j.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception:
        return None


def generate_listing_text(product: dict):
    """Return (title, tags, description, subtitle). Falls back to simple defaults if no API."""
    sku = product.get("sku") or "SKU"
    base = {
        "sku": sku,
        "name": product.get("name"),
        "description": product.get("description"),
        "audience": product.get("audience"),
        "niche": product.get("niche"),
        "style": product.get("style"),
    }
    prompt = (
        "Write Etsy-optimized listing copy as JSON with keys: "
        "title (<= 140 chars), tags (<= 13, lowercase), description (<= 1200 chars), subtitle (<= 90 chars).\n"
        "Use concise, high-intent keywords and avoid buzzwords.\n"
        "Input: " + json.dumps(base, ensure_ascii=False)
    )
    content = _chat(prompt)
    if content:
        try:
            text = content.strip()
            if text.startswith("```"):
                text = "\n".join([line for line in text.splitlines() if not line.strip().startswith("```")])
            j = json.loads(text)
            title = (j.get("title") or product.get("name") or sku)[:140]
            tags = j.get("tags") or []
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            tags = [t.lower()[:20] for t in tags][:13]
            desc = (j.get("description") or product.get("description") or "").strip()[:1200]
            sub = (j.get("subtitle") or "").strip()[:90]
            return title, tags, desc, sub
        except Exception:
            pass
    # Fallback
    title = product.get("name") or f"{sku}"
    tags = [t for t in (product.get("tags") or [])][:13]
    desc = (product.get("description") or title)[:1200]
    sub = title[:90]
    return title, tags, desc, sub

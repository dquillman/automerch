import os
import json
from collections import Counter
from statistics import median
from typing import Any, Dict, List, Tuple

from etsy_client import search_listings


def _extract_prices(listings: List[dict]) -> List[float]:
    prices: List[float] = []
    for item in listings:
        try:
            price = item.get("price") or {}
            amount = price.get("amount")
            # Etsy returns cents; ensure float dollars
            if amount is not None:
                prices.append(float(amount) / 100.0)
        except Exception:
            continue
    return [p for p in prices if p > 0]


def _tag_counts(listings: List[dict]) -> Counter:
    tags: List[str] = []
    for item in listings:
        t = item.get("tags") or []
        if isinstance(t, list):
            for tag in t:
                if isinstance(tag, str) and tag.strip():
                    tags.append(tag.strip().lower())
    return Counter(tags)


def basic_market_metrics(listings: List[dict]) -> Dict[str, Any]:
    count = len(listings)
    prices = _extract_prices(listings)
    prices_sorted = sorted(prices)
    p25 = prices_sorted[int(0.25 * (len(prices_sorted) - 1))] if prices_sorted else None
    p75 = prices_sorted[int(0.75 * (len(prices_sorted) - 1))] if prices_sorted else None
    med = median(prices_sorted) if prices_sorted else None
    avg = (sum(prices_sorted) / len(prices_sorted)) if prices_sorted else None
    tag_counter = _tag_counts(listings)
    top_tags = tag_counter.most_common(20)
    titles = [str((item.get("title") or "")).strip() for item in listings[:20]]
    titles = [t for t in titles if t]

    # Crude competition score: more results and tight pricing imply competition
    # Scale 0-100 where higher means more competitive (lower opportunity)
    comp_count = min(count / 500.0, 1.0)  # 0..1 for up to 500 results
    spread = 0.0
    if p25 is not None and p75 is not None and med not in (None, 0):
        spread = min(((p75 - p25) / (med if med else 1.0)), 2.0) / 2.0  # 0..1
    competition_score = round(100.0 * (0.7 * comp_count + 0.3 * (1.0 - spread)), 1)

    return {
        "total_listings": count,
        "prices": {
            "count": len(prices_sorted),
            "avg": round(avg, 2) if avg is not None else None,
            "median": round(med, 2) if med is not None else None,
            "p25": round(p25, 2) if p25 is not None else None,
            "p75": round(p75, 2) if p75 is not None else None,
            "min": round(prices_sorted[0], 2) if prices_sorted else None,
            "max": round(prices_sorted[-1], 2) if prices_sorted else None,
        },
        "top_tags": [(k, v) for k, v in top_tags],
        "example_titles": titles,
        "competition_score": competition_score,
    }


def _tokenize_title(t: str) -> List[str]:
    t = t.lower()
    junk = ",.!?:;{}[]()'\"/|\\+*&^%$#@`~"
    for ch in junk:
        t = t.replace(ch, " ")
    parts = [p for p in t.split() if p and p.isascii()]
    return parts


def _ngrams(words: List[str], n: int) -> List[Tuple[str, ...]]:
    return [tuple(words[i:i+n]) for i in range(0, max(0, len(words)-n+1))]


def derive_themes(listings: List[dict]) -> Dict[str, Any]:
    titles = [str((l.get("title") or "")).strip() for l in listings]
    titles = [t for t in titles if t]
    bigram_counter: Counter = Counter()
    trigram_counter: Counter = Counter()
    word_counter: Counter = Counter()
    for t in titles:
        words = _tokenize_title(t)
        word_counter.update(w for w in words if len(w) > 2)
        bigram_counter.update(_ngrams(words, 2))
        trigram_counter.update(_ngrams(words, 3))

    # Convert ngrams to strings
    top_bi = [(" ".join(k), v) for k, v in bigram_counter.most_common(30)]
    top_tri = [(" ".join(k), v) for k, v in trigram_counter.most_common(30)]

    # Identify potential audiences by simple keyword cues
    audience_keywords = [
        "mom","dad","teacher","nurse","engineer","gamer","cat","dog","retiree","student",
        "christmas","halloween","valentine","birthday","coworker","best friend","husband","wife",
    ]
    audience_hits: Counter = Counter()
    for w, c in word_counter.most_common(200):
        if w in audience_keywords:
            audience_hits[w] = c

    # Rare tags: bottom quartile among non-trivial tags
    tag_counts = _tag_counts(listings)
    tag_items = [(k, v) for k, v in tag_counts.items() if v >= 1]
    if tag_items:
        counts_sorted = sorted(v for _, v in tag_items)
        q1 = counts_sorted[max(0, int(0.25 * (len(counts_sorted)-1)))]
        rare_tags = [k for k, v in tag_items if v <= q1][:20]
    else:
        rare_tags = []

    return {
        "top_bigrams": top_bi,
        "top_trigrams": top_tri,
        "audience_signals": list(audience_hits.most_common(15)),
        "rare_tags": rare_tags,
        "top_words": word_counter.most_common(50),
        "top_tags": _tag_counts(listings).most_common(50),
        "top_titles": titles[:20],
    }


def _llm_chat_completion(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    model = os.getenv("OPENAI_MODEL", "gpt-5")

    # Try official SDK first; fall back to raw HTTP if not installed
    try:
        import openai  # type: ignore

        client = openai.OpenAI(api_key=api_key) if hasattr(openai, "OpenAI") else None
        if client:  # new SDK
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an Etsy product research expert. Reply with compact JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return resp.choices[0].message.content if resp.choices else None
        else:  # legacy SDK
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an Etsy product research expert. Reply with compact JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return completion["choices"][0]["message"]["content"]
    except Exception:
        pass

    # Fallback: raw HTTP
    try:
        import requests

        url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an Etsy product research expert. Reply with compact JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        r = requests.post(url, headers=headers, json=body, timeout=60)
        if r.status_code >= 400:
            return None
        j = r.json()
        return j.get("choices", [{}])[0].get("message", {}).get("content")
    except Exception:
        return None


def llm_synthesis(keywords: str, metrics: Dict[str, Any], sample_listings: List[dict]) -> Dict[str, Any]:
    """Ask an LLM to produce a research summary. Returns parsed JSON or {}."""
    guide = {
        "schema": {
            "summary": "string",
            "methodology": "string",
            "opportunity_score": "number (0-100, higher=better)",
            "price_recommendation": {"min": "number", "max": "number"},
            "recommended_tags": ["up to 13 strings"],
            "niches": ["strings"],
            "risks": ["strings"],
            "design_blueprints": [
                {
                    "name": "short unique slug",
                    "on_art_text": "exact text to print",
                    "visuals": ["specific elements (e.g., 'line-art cat', '80s grid', 'coffee steam swirls')"],
                    "style": "e.g., hand-lettered vintage, kawaii chibi, minimal mono-line",
                    "colors": ["hex or color names"],
                    "print_area": "mug 11oz front center | unisex tee chest | etc.",
                    "target_audience": "specific persona",
                    "primary_tags": ["<=7 tags"],
                    "notes": "production/layout constraints",
                }
            ],
        },
        "constraints": [
            "Avoid generic ideas; be concrete and actionable",
            "Include exact on_art_text for each design",
            "Base designs on provided themes and avoid overused phrases from top_titles",
            "Prefer niches indicated by rare_tags and audience_signals",
            "Return strictly valid JSON only (no markdown fences)",
            "8-12 design_blueprints",
        ],
    }

    prompt = (
        "You are an Etsy POD research expert. Produce SPECIFIC design concepts.\n"
        f"Query: {keywords}\n\n"
        "Observed market metrics (JSON):\n" + json.dumps(metrics, ensure_ascii=False) + "\n\n"
        "Derived themes (JSON):\n" + json.dumps(derive_themes(sample_listings), ensure_ascii=False) + "\n\n"
        "Sample listings (top 10, JSON):\n" + json.dumps([
            {"title": l.get("title"), "price": l.get("price"), "tags": l.get("tags")}
            for l in sample_listings[:10]
        ], ensure_ascii=False) + "\n\n"
        "Return a single JSON object strictly matching this schema:\n" + json.dumps(guide["schema"]) + "\n\n"
        "Constraints:\n- " + "\n- ".join(guide["constraints"]) + "\n"
    )

    content = _llm_chat_completion(prompt)
    if not content:
        return {}
    # Extract JSON if the model wrapped it in fencing
    try:
        text = content.strip()
        if text.startswith("```"):
            # remove fences
            text = "\n".join([line for line in text.splitlines() if not line.strip().startswith("```")])
        return json.loads(text)
    except Exception:
        return {"raw": content}


def run_research(keywords: str, limit: int = 50) -> Dict[str, Any]:
    """Run complete research including downloading and storing competitor images."""
    import requests
    import base64
    from pathlib import Path
    import os
    
    # Create images directory if it doesn't exist
    images_dir = Path("research_images")
    images_dir.mkdir(exist_ok=True)
    
    listings = search_listings(keywords, limit=limit)
    metrics = basic_market_metrics(listings)
    llm = llm_synthesis(keywords, metrics, listings)
    preview = []
    
    for l in listings[:20]:
        # Extract image URLs from listing - Etsy API returns images in various formats
        images = []
        image_url = None
        
        # Try multiple possible image field locations
        if l.get("images") and isinstance(l["images"], list) and len(l["images"]) > 0:
            # List of image objects
            for img in l["images"]:
                if isinstance(img, dict):
                    # Try common Etsy image URL fields (prioritize larger sizes)
                    img_url = (img.get("url_fullxfull") or 
                              img.get("url_570xN") or 
                              img.get("url_340x270") or 
                              img.get("url_75x75") or 
                              img.get("url"))
                    if img_url:
                        images.append({"url": img_url})
                elif isinstance(img, str):
                    images.append({"url": img})
        elif l.get("images") and isinstance(l["images"], dict):
            # Single image object
            img_url = (l["images"].get("url_fullxfull") or 
                      l["images"].get("url_570xN") or 
                      l["images"].get("url"))
            if img_url:
                images.append({"url": img_url})
        
        # Try direct image URL fields
        if not images:
            for field in ["url_fullxfull", "url_570xN", "url_340x270", "url_75x75", "url", "image_url", "primary_image"]:
                if l.get(field):
                    images.append({"url": l[field]})
                    break
        
        # Get primary image (first one found)
        image_url = None
        if images and len(images) > 0:
            if isinstance(images[0], dict):
                image_url = images[0].get("url")
            elif isinstance(images[0], str):
                image_url = images[0]
        
        # Download and store primary image for image-to-image generation
        local_image_path = None
        image_data_base64 = None
        relative_path = None
        
        # Create unique filename
        listing_id = l.get("listing_id") or f"listing_{len(preview)}"
        safe_title = "".join(c for c in (l.get("title") or "product")[:50] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        
        # Function to create placeholder image
        def create_placeholder_image(output_path: Path, title: str, listing_id_val) -> tuple:
            """Create a placeholder image locally."""
            try:
                from PIL import Image, ImageDraw, ImageFont
                import io
                
                # Create 800x800 image with gradient background
                img = Image.new('RGB', (800, 800), color=(70, 130, 180))
                draw = ImageDraw.Draw(img)
                
                # Draw title
                title_text = title[:40] if title else f"Product {listing_id_val}"
                try:
                    # Try default font first
                    font = ImageFont.load_default()
                except:
                    font = None
                
                # Get text size
                if font:
                    bbox = draw.textbbox((0, 0), title_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:
                    text_width = len(title_text) * 10
                    text_height = 20
                
                # Center text
                position = ((800 - text_width) // 2, (800 - text_height) // 2)
                draw.text(position, title_text, fill=(255, 255, 255), font=font)
                
                # Save image
                img.save(output_path, 'JPEG', quality=85)
                
                # Convert to base64
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG')
                img_bytes.seek(0)
                base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
                
                # Use absolute path or relative path that works on Windows
                try:
                    rel_path = str(output_path.relative_to(Path.cwd()))
                except ValueError:
                    # If relative path fails, use absolute path
                    rel_path = str(output_path)
                return rel_path, base64_data
            except ImportError:
                print(f"[Research] PIL/Pillow not installed. Install with: pip install Pillow")
                return None, None
            except Exception as e:
                print(f"[Research] Error creating placeholder: {e}")
                return None, None
        
        if image_url and (image_url.startswith("http://") or image_url.startswith("https://")):
            try:
                print(f"[Research] Downloading image from: {image_url[:80]}...")
                response = requests.get(image_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                print(f"[Research] Response status: {response.status_code}")
                if response.status_code == 200:
                    # Get file extension from URL or content type
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    ext = 'jpg'
                    if 'png' in content_type:
                        ext = 'png'
                    elif 'webp' in content_type:
                        ext = 'webp'
                    elif image_url.lower().endswith('.png'):
                        ext = 'png'
                    elif image_url.lower().endswith('.webp'):
                        ext = 'webp'
                    
                    filename = f"{listing_id}_{safe_title}.{ext}"
                    local_image_path = images_dir / filename
                    
                    # Save image locally
                    local_image_path.write_bytes(response.content)
                    print(f"[Research] Saved image: {local_image_path} ({len(response.content)} bytes)")
                    
                    # Convert to base64 for API
                    image_data_base64 = base64.b64encode(response.content).decode('utf-8')
                    print(f"[Research] Base64 length: {len(image_data_base64)} chars")
                    
                    # Store local path relative to project root
                    try:
                        relative_path = str(local_image_path.relative_to(Path.cwd()))
                    except ValueError:
                        # If relative path fails, use absolute path
                        relative_path = str(local_image_path)
                else:
                    raise Exception(f"HTTP {response.status_code}")
            except Exception as e:
                # If download fails, create placeholder image
                print(f"[Research] Download failed, creating placeholder image...")
                filename = f"{listing_id}_{safe_title}_placeholder.jpg"
                placeholder_path = images_dir / filename
                relative_path, image_data_base64 = create_placeholder_image(
                    placeholder_path, 
                    l.get("title") or "Product", 
                    listing_id
                )
                if relative_path:
                    local_image_path = placeholder_path
                    print(f"[Research] Created placeholder: {local_image_path}")
        else:
            # No image URL - create placeholder
            if not image_url:
                print(f"[Research] No image URL found, creating placeholder...")
            filename = f"{listing_id}_{safe_title}_placeholder.jpg"
            placeholder_path = images_dir / filename
            relative_path, image_data_base64 = create_placeholder_image(
                placeholder_path,
                l.get("title") or "Product",
                listing_id
            )
            if relative_path:
                local_image_path = placeholder_path
                print(f"[Research] Created placeholder: {local_image_path}")
        
        # Extract price amount
        price_obj = l.get("price")
        price = None
        if isinstance(price_obj, dict):
            amount = price_obj.get("amount")
            if amount:
                price = float(amount) / 100.0 if amount > 100 else float(amount)  # Assume cents if > 100
        elif isinstance(price_obj, (int, float)):
            price = float(price_obj)
        
        preview.append({
            "listing_id": l.get("listing_id"),
            "title": l.get("title"),
            "description": l.get("description"),
            "price": price,
            "currency": l.get("price", {}).get("currency_code") if isinstance(l.get("price"), dict) else "USD",
            "tags": l.get("tags", []),
            "views": l.get("views"),
            "num_favorers": l.get("num_favorers"),
            "url": l.get("url") or (f"https://www.etsy.com/listing/{l.get('listing_id')}" if l.get('listing_id') else None),
            "images": images,
            "image_url": image_url,
            "image_local_path": relative_path,  # Local file path
            "image_data_base64": image_data_base64,  # Base64 for API
        })
    return {"keywords": keywords, "metrics": metrics, "llm": llm, "listings": preview}

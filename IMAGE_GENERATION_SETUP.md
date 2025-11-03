# Image Generation Setup Guide

## 🎨 Overview

AutoMerch Lite now supports AI-powered image generation for product designs using Google Gemini, OpenAI DALL-E, or Stability AI.

## 🔧 Configuration

### Option 1: Google Gemini Image Generation
**Note:** Google Gemini now includes image generation (via gemini-2.0-flash-exp model).

**Setup:**
1. Get API key from: https://makersuite.google.com/app/apikey
2. Install package:
   ```bash
   pip install google-genai
   ```
3. Set environment variable:
   ```bash
   export GOOGLE_API_KEY=your_api_key_here
   ```
4. Set provider:
   ```bash
   export IMAGE_GEN_PROVIDER=google_imagen
   ```

**Alternative:** Use OpenAI DALL-E (easier setup, see Option 2 below)

### Option 2: OpenAI DALL-E
1. Get API key from: https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
3. Set provider:
   ```bash
   export IMAGE_GEN_PROVIDER=openai_dalle
   ```

### Option 3: Stability AI
1. Get API key from: https://platform.stability.ai/
2. Set environment variable:
   ```bash
   export STABILITY_API_KEY=your_api_key_here
   ```
3. Set provider:
   ```bash
   export IMAGE_GEN_PROVIDER=stability_ai
   ```

## 📦 Install Dependencies

For Google Imagen (Vertex AI):
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-cloud-aiplatform
```

**Recommended:** Use OpenAI DALL-E (easier setup):
```bash
pip install openai
```

For OpenAI DALL-E:
```bash
pip install openai
```

For Stability AI:
```bash
pip install requests  # Already installed
```

## 🚀 Usage

1. **Run Research** - Go to `/research` and search for keywords
2. **View Details** - Click "View Full Research Details" to see all data including competitor images
3. **Generate Images** - Click "Generate 5 Better Images" button
4. **Download/Use** - Download images or use them directly in product creation

## 📄 API Endpoints

### Generate from Research
```bash
POST /api/images/generate-from-research
{
  "keywords": "coffee mug",
  "research_data": { /* full research results */ },
  "count": 5,
  "style": "professional"
}
```

### Generate from Prompt
```bash
POST /api/images/generate
{
  "prompt": "coffee mug design with adventure theme",
  "count": 5,
  "style": "professional",
  "aspect_ratio": "1:1",
  "research_data": { /* optional */ }
}
```

## 🎯 Features

- ✅ Research-based image generation (uses market insights)
- ✅ Multiple style options (professional, artistic, minimal, vibrant, modern)
- ✅ Competitor image viewing
- ✅ Direct integration with product creation
- ✅ Download generated images
- ✅ Dry-run mode for testing (uses placeholder images)

## 💡 Tips

- Generated images are optimized using research insights
- Images use competitor analysis and AI recommendations
- Can generate up to 5 variations at once
- Images are automatically sized for product listings (1:1 aspect ratio)


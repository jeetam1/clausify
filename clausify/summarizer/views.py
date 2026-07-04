# summarizer/views.py
import json
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from google import genai


@ensure_csrf_cookie
def index(request):
    return render(request, 'summarizer/index.html')


@require_POST
def summarize(request):
    """
    1. Receive URL from frontend (JSON body)
    2. Scrape the page text with requests + BeautifulSoup
    3. Send text to Gemini with a clear prompt
    4. Return structured JSON summary to frontend
    """
    try:
        body = json.loads(request.body)
        url = body.get('url', '').strip()

        if not url:
            return JsonResponse({'error': 'No URL provided.'}, status=400)

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # ── Step 1: Scrape page text ──────────────────────────────────
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; Clausify/1.0)'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return JsonResponse({'error': 'The website took too long to respond. Try again.'}, status=408)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Could not reach that URL: {str(e)}'}, status=400)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove nav, footer, script, style noise
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()

        raw_text = soup.get_text(separator=' ', strip=True)

        # Truncate to ~12,000 chars to stay within token limits
        text_to_analyze = raw_text[:12000]

        if len(text_to_analyze) < 200:
            return JsonResponse(
                {'error': 'Not enough text found on that page. Try a direct link to the T&C page.'},
                status=400
            )

        # ── Step 2: Call Gemini API ───────────────────────────────────
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        prompt = f"""You are a legal document analyst. A user has pasted the text of a Terms & Conditions, Privacy Policy, or similar legal document.

Analyze the text below and return a JSON object with EXACTLY this structure (no markdown, no code fences, raw JSON only):

{{
  "site_name": "name of the website or service",
  "one_liner": "one sentence plain-English summary of what this document covers",
  "risk_level": "low" | "medium" | "high",
  "risk_reason": "one sentence explaining the risk level",
  "key_points": [
    {{
      "type": "warning" | "good" | "info",
      "title": "short title (5 words max)",
      "detail": "one clear sentence explanation"
    }}
  ],
  "data_collected": ["list", "of", "data types collected"],
  "user_rights": ["list", "of", "rights the user has"],
  "watchout": "the single most important thing a user should know"
}}

Rules:
- key_points must have 4-6 items. Use "warning" for concerning clauses, "good" for user-friendly terms, "info" for neutral facts.
- Be direct and honest. Don't soften warnings.
- Write for a non-lawyer audience.

Document text:
{text_to_analyze}"""

        result = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        raw_response = result.text.strip()

        # Strip any accidental markdown code fences
        if raw_response.startswith('```'):
            raw_response = raw_response.split('```')[1]
            if raw_response.startswith('json'):
                raw_response = raw_response[4:]
        raw_response = raw_response.strip()

        summary = json.loads(raw_response)

        return JsonResponse({'success': True, 'summary': summary})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'AI returned an unexpected format. Please try again.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)
import json
from urllib.parse import quote

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import ShortenedURL


def check_url_safety(url):
    """
    Returns one of: 'Safe & Secure', 'Unsafe / Phishing Detected', 'Unable to verify'
    Never raises — always returns a status string.
    """
    api_key = settings.SAFE_BROWSING_API_KEY
    if not api_key:
        return "Unable to verify"

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    payload = {
        "client": {"clientId": "url-shortener-app", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE", "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("matches"):
            return "Unsafe / Phishing Detected"
        return "Safe & Secure"
    except requests.exceptions.RequestException:
        # Covers timeouts, connection errors, bad status codes — never crash the view
        return "Unable to verify"


def create_short_url(request):
    short_url = None
    qr_code_url = None
    safety_status = None
    short_code = None

    if request.method == 'POST':
        long_url = request.POST.get('long_url', '').strip()

        if not long_url:
            context = {'error': 'Please enter a valid URL'}
            return render(request, 'shortener/index.html', context)

        safety_status = check_url_safety(long_url)

        if safety_status == "Unsafe / Phishing Detected":
            context = {'error': 'This URL was flagged as unsafe and was not shortened.'}
            return render(request, 'shortener/index.html', context)
        # "Unable to verify" is allowed through — we don't block shortening just because
        # the safety check itself failed, we just show a neutral badge instead of a false "safe"

        new_link = ShortenedURL.objects.create(long_url=long_url)
        short_code = new_link.short_code

        short_url = request.build_absolute_uri('/') + short_code
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote(short_url, safe='')}"

    context = {
        'short_url': short_url,
        'qr_code_url': qr_code_url,
        'safety_status': safety_status,
        'short_code': short_code,  # for the "View details" link
    }
    return render(request, 'shortener/index.html', context)


def redirect_url(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.long_url)


def link_details(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    short_url = request.build_absolute_uri('/') + short_code
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote(short_url, safe='')}"

    context = {
        'short_url': short_url,
        'qr_code_url': qr_code_url,
        'long_url': url_obj.long_url,
        'clicks': url_obj.clicks,
        'created_at': url_obj.created_at,
    }
    return render(request, 'shortener/details.html', context)


def check_safety_only(request):
    """Standalone endpoint: check a URL's safety without shortening it."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    url = data.get('url', '').strip()
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)

    status = check_url_safety(url)
    return JsonResponse({'safety_status': status})
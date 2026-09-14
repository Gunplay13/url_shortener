from django.shortcuts import render, redirect, get_object_or_404
from .models import ShortenedURL

def create_short_url(request):
    short_url = None
    qr_code_url = None
    safety_status = None

    if request.method == 'POST':
        long_url = request.POST.get('long_url', '').strip()

        if not long_url:
            context = {'error': 'Please enter a valid URL'}
            return render(request, 'shortener/index.html', context)

        # Safety check BEFORE saving
        if "badsite" in long_url:
            context = {'error': 'This URL was flagged as unsafe and was not shortened.'}
            return render(request, 'shortener/index.html', context)

        safety_status = "Safe & Secure"

        # Let the model generate the short_code (uses generate_short_code default)
        new_link = ShortenedURL.objects.create(long_url=long_url)
        short_code = new_link.short_code

        short_url = request.build_absolute_uri('/') + short_code
        qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={short_url}"

    context = {
        'short_url': short_url,
        'qr_code_url': qr_code_url,
        'safety_status': safety_status,
    }
    return render(request, 'shortener/index.html', context)


def redirect_url(request, short_code):
    url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.long_url)
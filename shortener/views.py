from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import ShortenedURL

def create_short_url(request):
    if request.method == "POST":
        original_url = request.POST.get("url")
        if not original_url:
            return JsonResponse({"error": "URL parameter missing"}, status=400)
        
        obj, created = ShortenedURL.objects.get_or_create(original_url=original_url)
        return JsonResponse({
            "short_code": obj.short_code,
            "short_url": request.build_absolute_uri(f"/{obj.short_code}")
        })
    return render(request, "shortener/index.html")

def redirect_url(request, short_code):
    url_item = get_object_or_404(ShortenedURL, short_code=short_code)
    url_item.clicks += 1
    url_item.save(update_fields=['clicks'])
    return redirect(url_item.original_url)

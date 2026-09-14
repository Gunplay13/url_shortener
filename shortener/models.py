from django.db import models
import random
import string


def generate_short_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))


class ShortenedURL(models.Model):
    long_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True, default=generate_short_code)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"
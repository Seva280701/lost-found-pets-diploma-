"""Serve uploaded media files in production (when DEBUG=False Django's static() returns 404)."""
import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


def serve_media(request, path):
    """Serve a file from MEDIA_ROOT. Safe against path traversal."""
    path = path.lstrip('/')
    if '..' in path or path.startswith('/'):
        raise Http404("Invalid path")
    media_root = Path(settings.MEDIA_ROOT).resolve()
    full_path = (media_root / path).resolve()
    try:
        full_path.relative_to(media_root)
    except ValueError:
        raise Http404("Invalid path")
    if not full_path.is_file():
        raise Http404("File not found")
    content_type, _ = mimetypes.guess_type(str(full_path))
    response = FileResponse(open(full_path, 'rb'), content_type=content_type or 'application/octet-stream')
    return response

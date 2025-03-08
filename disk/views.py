from django.core.cache import cache
import logging
import os
import requests
import urllib.parse
import zipfile
from io import BytesIO
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.conf import settings
from .yandex_api import get_files_from_public_link
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def index(request):
    """
    Главная страница приложения.
    """
    return render(request, 'disk/index.html')


def get_files(request):
    """
    Получает список файлов и папок с Яндекс.Диска по публичной ссылке.
    """
    public_key = request.GET.get('public_key')
    path = request.GET.get('path', '')  # Текущий путь

    if not public_key:
        return JsonResponse({'error': 'No public key provided'}, status=400)

    cache_key = f"yandex_files:{public_key}:{path}"
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info(f"Загрузка из кэша: {cache_key}")
        return JsonResponse(cached_data)

    files_data = get_files_from_public_link(public_key, path)

    if 'error' in files_data:
        return JsonResponse({
            'error': files_data['error']
        })

    available_extensions = set()
    file_list = []
    folder_list = []
    current_folder = files_data["name"]

    if '_embedded' in files_data and 'items' in files_data['_embedded']:
        for item in files_data['_embedded']['items']:
            file_name = item.get('name', 'Unknown')
            file_ext = os.path.splitext(file_name)[-1].lower()
            is_folder = item.get('type') == 'dir'
            full_path = item.get('path', '')

            if is_folder:
                folder_list.append({'name': file_name, 'path': full_path})
            else:
                if file_ext:
                    available_extensions.add(file_ext)
                file_list.append({
                    'name': file_name,
                    'file': item.get('file', None),
                    'extension': file_ext
                })
    response_data = {
        'files': file_list,
        'folders': folder_list,
        'current_folder': current_folder,
        'available_types': list(available_extensions)
    }

    cache.set(cache_key, response_data, settings.CACHE_TTL)
    return JsonResponse(response_data)



def download_file(request):
    """
    Позволяет скачивать один файл с Яндекс.Диска.
    """
    file_url = request.GET.get('file_url')
    file_name = request.GET.get('file_name')

    if not file_url or not file_name:
        return JsonResponse({'error': 'File URL and name are required'}, status=400)

    decoded_url = urllib.parse.unquote(file_url)
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    local_file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    response = requests.get(decoded_url, stream=True)
    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to download file'}, status=500)

    with open(local_file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return FileResponse(open(local_file_path, 'rb'), as_attachment=True, filename=file_name)


def download_multiple_files(request):
    """
    Позволяет скачивать несколько файлов в одном ZIP-архиве.
    """
    file_urls = request.GET.getlist('file_urls[]')
    file_names = request.GET.getlist('file_names[]')

    if not file_urls or not file_names or len(file_urls) != len(file_names):
        return JsonResponse({'error': 'Invalid file URLs or names'}, status=400)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_url, file_name in zip(file_urls, file_names):
            decoded_url = urllib.parse.unquote(file_url)
            response = requests.get(decoded_url, stream=True)
            if response.status_code == 200:
                file_data = response.content
                zip_file.writestr(file_name, file_data)

    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="downloaded_files.zip"'
    return response

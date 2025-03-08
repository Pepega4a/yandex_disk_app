import requests
from typing import Dict, Any, Optional

YANDEX_API_BASE_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

def get_files_from_public_link(public_key: str, path: Optional[str] = None) -> Dict[str, Any]:
    """
    Получает список файлов по публичной ссылке Яндекс.Диска.

    :param public_key: Публичная ссылка (ключ)
    :param path: Опциональный путь к папке на диске
    :return: Словарь с информацией о файлах
    """
    params = {'public_key': public_key}

    if path:
        params['path'] = path

    response = requests.get(YANDEX_API_BASE_URL, params=params)

    if response.status_code != 200:
        return {"error": f"Ошибка API Яндекс.Диска: {response.status_code} - {response.json().get('message')}"}
    
    return response.json()

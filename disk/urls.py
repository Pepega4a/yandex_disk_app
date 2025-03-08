from django.urls import path
from .views import index, get_files, download_file, download_multiple_files

urlpatterns = [
    path('', index, name='index'),
    path('get_files/', get_files, name='get_files'),
    path('download/', download_file, name='download_file'),
    path('download_multiple/', download_multiple_files, name='download_multiple'),
]

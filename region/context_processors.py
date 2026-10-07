from django.conf import settings


def carto_basemap(request):
    return {'carto_basemap_key': settings.CARTO_BASEMAP_API_KEY}

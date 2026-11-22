from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Scheme
from .serializers import SchemeSerializer

SCHEMES_LIST_CACHE_KEY = 'active_schemes_list'
SCHEME_DETAIL_CACHE_PREFIX = 'scheme_detail_'

class SchemeListView(APIView):
    def get(self, request):
        cached = cache.get(SCHEMES_LIST_CACHE_KEY)
        if cached is not None:
            return Response({"schemes": cached})

        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')
        serializer = SchemeSerializer(schemes, many=True)
        data = serializer.data
        cache.set(SCHEMES_LIST_CACHE_KEY, data, 300)
        return Response({"schemes": data})

class SchemeDetailView(APIView):
    def get(self, request, code):
        cache_key = f"{SCHEME_DETAIL_CACHE_PREFIX}{code}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        try:
            scheme = Scheme.objects.prefetch_related('document_requirements__document').get(code=code, is_active=True)
            serializer = SchemeSerializer(scheme)
            data = serializer.data
            cache.set(cache_key, data, 300)
            return Response(data)
        except Scheme.DoesNotExist:
            return Response({"error": "Scheme not found"}, status=status.HTTP_404_NOT_FOUND)

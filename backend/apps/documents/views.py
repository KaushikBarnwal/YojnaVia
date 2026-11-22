from rest_framework.views import APIView
from rest_framework.response import Response
from .graph import DocumentGraphService
from .models import Document

class DocumentDependencyGraphView(APIView):
    def get(self, request):
        graph = DocumentGraphService.get_document_dependency_graph()
        return Response(graph)

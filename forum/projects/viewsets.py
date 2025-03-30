from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from elasticsearch_dsl import Q
from .documents import ProjectDocument
from .serializers import ProjectSearchSerializer


class ProjectSearchView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]
    document = ProjectDocument
    serializer_class = ProjectSearchSerializer
    page_size = 10

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING)
        ],
        responses={
            200: ProjectSearchSerializer(many=True),
            500: openapi.Response(description="Search failed")
        }
    )
    def get(self, request):
        try:
            query = request.GET.get('q', '')
            status_filter = request.GET.get('status', None)

            # Base search query
            search = self.document.search()

            # Multi-match query with fuzziness
            if query:
                search = search.query(
                    Q('multi_match',
                      query=query,
                      fields=['title^3', 'description'],
                      fuzziness='AUTO')
                )

            # Status filter
            if status_filter:
                search = search.filter('term', status=status_filter.lower())

            # Execute search and paginate
            response = search.execute()
            results = self.paginate_queryset(response, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"error": "Search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

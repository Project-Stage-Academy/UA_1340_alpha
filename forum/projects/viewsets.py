from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from elasticsearch_dsl import Q
from django.db.models import Case, When

from .documents import ProjectDocument
from .serializers import ProjectSearchSerializer
from .models import Project


class ProjectSearchView(APIView, PageNumberPagination):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSearchSerializer
    page_size = 10
    document = ProjectDocument

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

            # Build Elasticsearch query
            search = self.document.search()

            # Multi-match with fuzziness for search
            if query:
                search = search.query(
                    Q('multi_match',
                      query=query,
                      fields=['title^3', 'description'],
                      fuzziness='AUTO')
                )

            # Apply status filter
            if status_filter:
                search = search.filter('term', status=status_filter.lower())

            # Execute search and get ordered IDs
            response = search.execute()
            project_ids = [hit.meta.id for hit in response]

            # Preserve Elasticsearch ordering using Case/When
            preserved_order = Case(
                *[When(id=id, then=pos) for pos, id in enumerate(project_ids)]
            )

            # Get actual Django objects with proper ordering
            queryset = Project.objects.filter(id__in=project_ids) \
                .order_by(preserved_order) \
                .select_related('startup')

            # Paginate and serialize
            paginated_queryset = self.paginate_queryset(queryset, request, view=self)
            serializer = self.serializer_class(paginated_queryset, many=True)

            return self.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {"error": "Search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

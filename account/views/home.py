from account.models import Member
from account.serializers import MemberSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User

class HomeView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        return Response(template_name='base.html')
    
class MemberView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'account/member.html'

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Get member with the id", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Get all the members",
                schema=MemberSerializer(many=True)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:

            id = request.query_params.get('id')

            queryset = Member.objects.all().order_by('id')
            if id:
                queryset = queryset.filter(id=id)
            
            if request.accepted_renderer.format == 'html':
                paginator = Paginator(queryset, 10)  # Limit of 6 items per page
                page_number = request.query_params.get('page', 1)
                page_obj = paginator.get_page(page_number)
                return Response({
                    'Members': page_obj,
                }, template_name=self.template_name)
            
            serializer = MemberSerializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @swagger_auto_schema(
        request_body=MemberSerializer,
        responses={
            201: openapi.Response(
                description="Member created successfully",
                schema=MemberSerializer()
            ),
            400: "Bad Request",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = MemberSerializer(data=data)

            if serializer.is_valid():
                serializer.save()

                if request.accepted_renderer.format == 'html':
                    return JsonResponse(
                        {
                            "status": status.HTTP_200_OK,
                            "message": "Member created successfully!",
                            "data": {
                                'member': serializer.data
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response({
                    "status": status.HTTP_201_CREATED,
                    "message": "Member created successfully!",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error:", e)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @swagger_auto_schema(
        request_body=MemberSerializer,
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the member to update", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Member updated successfully",
                schema=MemberSerializer()
            ),
            400: openapi.Response(description="Invalid data or ID not provided"),
            404: openapi.Response(description="Member not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            member_id = request.query_params.get('id')
            if not member_id:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                member_id = int(member_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            member = Member.objects.filter(id=member_id).first()
            if not member:
                return Response({"error": "Rental-log not found"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data

            if data:
                serializer = MemberSerializer(member,data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Member updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "No changes detected."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the member to delete", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Member deleted successfully"),
            400: openapi.Response(description="ID must be provided"),
            404: openapi.Response(description="Member not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            id = request.query_params.get('id')

            if not id:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            member = Member.objects.filter(id=id).first()
            if not member:
                return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

            member.delete()

            return Response( status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




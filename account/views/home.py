from account.models import Member
from account.serializers import MemberSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import JsonResponse

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

            queryset = Member.objects.all()
            if id:
                queryset = queryset.filter(id=id)
            
            if request.accepted_renderer.format == 'html':
                return Response({"Members":queryset},template_name=self.template_name)

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



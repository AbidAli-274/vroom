from datetime import timezone
from account.models import Member
from account.serializers import MemberSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status


class SignupView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="A JSON response with a list of all members",
                schema=MemberSerializer(many=True)
            )
        }
    )
    def get(self, request, *args, **kwargs):

        if request.accepted_renderer.format == 'html':
            # Render HTML template if the requested format is HTML
            # data = {'users': queryset}  # Pass data to the template if needed
            return Response(template_name='account/signup.html')
        
        # Return JSON data if the requested format is JSON
        serializer = MemberSerializer(many=True) 
        return Response(serializer.data)
    
class HomeView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        return Response(template_name='base.html')
    
class MemberView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

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
            historical = request.query_params.get('historical')

            queryset = Member.objects.all()
            if id:
                queryset = queryset.filter(id=id)

            if request.accepted_renderer.format == 'html':
                return Response({'rental_logs': queryset}, template_name='account/create_member.html')

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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )



from account.models import DocumentStorage, Member
from account.serializers import DocumentStorageSerializer, MemberSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils.datastructures import MultiValueDict
import cloudinary
import cloudinary.uploader
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
            # Include file URLs for each member in the serialized data
            member_data = serializer.data
            for i, member in enumerate(member_data):
                member_files = DocumentStorage.objects.filter(member_id=member['id']).values('image')
                member_data[i]['files'] = [file['image'] for file in member_files]
            
            return Response(member_data)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'nric': openapi.Schema(type=openapi.TYPE_STRING),
                'dob': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                'class_passed': openapi.Schema(type=openapi.TYPE_STRING),
                'issue_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                'remarks': openapi.Schema(type=openapi.TYPE_STRING),
                'address': openapi.Schema(type=openapi.TYPE_STRING),
                'file': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),  
                    description="Upload one or more file URLs"
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Member created successfully",
                schema=MemberSerializer
            ),
            400: "Bad Request",
            500: "Internal Server Error",
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            
            serializer = MemberSerializer(data=data)

            files = request.FILES.getlist('file') 

            file_urls = []  

            if files:
                cloudinary.config(
                    cloud_name='daj0lzvak',
                    api_key='222713357542916',
                    api_secret='fyA1-yiKYPoL0ODKUWfqNse-D54',
                )

                # Upload each file to Cloudinary
                for file in files:
                    cloudinary_file = cloudinary.uploader.upload(file, use_filename=True, resource_type='raw')
                    file_url = cloudinary_file['url']
                    file_urls.append(file_url)

            if serializer.is_valid():
                member = serializer.save()

                member_data = serializer.data

                if files:
                    for file_url in file_urls:
                        document_data = {
                            'image': file_url,
                            'member': member.id
                        }
                        document_serializer = DocumentStorageSerializer(data=document_data)

                        if document_serializer.is_valid():
                            document_serializer.save()

                    member_data['files'] = file_urls
                else:
                    member_data['files'] = []  

                if request.accepted_renderer.format == 'html':
                    return JsonResponse(
                        {
                            "status": status.HTTP_200_OK,
                            "message": "Member created successfully with files!" if files else "Member created successfully without files.",
                            "data": {
                                'member': member_data
                            },
                        },
                        status=status.HTTP_200_OK,
                    )

                return Response({
                    "status": status.HTTP_201_CREATED,
                    "message": "Member created successfully with files!" if files else "Member created successfully without files.",
                    "data": member_data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'full_name': openapi.Schema(type=openapi.TYPE_STRING),
            'phone': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'nric': openapi.Schema(type=openapi.TYPE_STRING),
            'dob': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            'class_passed': openapi.Schema(type=openapi.TYPE_STRING),
            'issue_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            'remarks': openapi.Schema(type=openapi.TYPE_STRING),
            'address': openapi.Schema(type=openapi.TYPE_STRING),
            'file': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                description="Optional: Provide an array of file URLs to update the member's files"
            ),
        },
    ),
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description="ID of the member to update", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: openapi.Response(
            description="Member updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
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
                return Response({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data
            files=[]
            if 'file' in data:
                if isinstance(data, MultiValueDict):
                    files = data.getlist('file') 
                else:
                    files = data.get('file', [])
            else:
                files = request.FILES.getlist('file')  

            new_file_urls = []  

            if files:
                cloudinary.config(
                    cloud_name='daj0lzvak',
                    api_key='222713357542916',
                    api_secret='fyA1-yiKYPoL0ODKUWfqNse-D54',
                )

                for file in files:
                    cloudinary_file = cloudinary.uploader.upload(file, use_filename=True, resource_type='raw')
                    new_file_urls.append(cloudinary_file['url'])

            if data:
                serializer = MemberSerializer(member, data=data, partial=True)
                if serializer.is_valid():
                    member = serializer.save()

                    if new_file_urls:
                        for file_url in new_file_urls:
                            document_data = {
                                'image': file_url,
                                'member': member.id
                            }
                            document_serializer = DocumentStorageSerializer(data=document_data)
                            if document_serializer.is_valid():
                                document_serializer.save()

                        serializer_data = serializer.data
                        serializer_data['files'] = new_file_urls
                        return Response({"message": "Member updated successfully with files!", "data": serializer_data}, status=status.HTTP_200_OK)
                    else:
                        serializer_data = serializer.data
                        serializer_data['files'] = []  
                        return Response({"message": "Member updated successfully without files.", "data": serializer_data}, status=status.HTTP_200_OK)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"message": "No changes detected."}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
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




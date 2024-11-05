from urllib.request import Request
from account.models import Member
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from account.serializers import  UserSerializer
from account.utils import get_user_by_email_or_username
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
class SignupView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'account/signup.html'
    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)
    
    @swagger_auto_schema(
        
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="First name"),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Last name"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
            },
            required=['first_name', 'last_name', 'email', 'password']
        ),
        responses={
            201: "User created successfully",
            400: "Invalid data provided"
        },
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        try:
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            password = request.data.get('password')
            if not all([first_name, last_name, email, password]):
                print('Missing fields:', request.data)  
                return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
            base_username = f"{first_name.lower()}"
            similar_users_count = User.objects.filter(username__startswith=base_username).count()
            username = f"{base_username}{similar_users_count + 1}"
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "password": make_password(password)
            }
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                serializer.save()
                success_data = {'message': 'User created successfully', 'username': username}
                if request.accepted_renderer.format == 'html':
                    return Response(success_data, template_name=self.template_name, status=status.HTTP_201_CREATED)
                return Response(success_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLogin(APIView):
    
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'account/login.html'
    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        return Response(template_name=self.template_name)
    
    @swagger_auto_schema(
        operation_description="API endpoint for user login. Validates user credentials and returns auth tokens if "
        "successful.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email_or_username", "password"],
            properties={
                "email_or_username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User email or username"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User password"
                ),
            },
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful login", schema=UserSerializer()
            ),
            status.HTTP_422_UNPROCESSABLE_ENTITY: openapi.Response(
                description="Login failed due to incorrect credentials"
            ),
            status.HTTP_403_FORBIDDEN: openapi.Response(
                description="Email is not verified."
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="User not found"),
        },
        tags=["Authentication"],
    )

    def post(self, request: Request) -> JsonResponse:
        try:
            email_or_username: str = request.data.get("email_or_username", "").lower()
            password: str = request.data.get("password")

            if not (email_or_username and password):
                return JsonResponse(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "error": "Please enter all fields",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = get_user_by_email_or_username(email_or_username)
            if not user:
                return JsonResponse(
                    {
                        "status": status.HTTP_404_NOT_FOUND,
                        "error": "User does not exist",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not check_password(password, user.password):
                return JsonResponse(
                    {
                        "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "error": "Incorrect password",
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            login(request, user)
            refresh = RefreshToken.for_user(user)
            return JsonResponse(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Login success",
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "user": UserSerializer(user).data,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserLogout(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'account/login.html'
    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        logout(request)
        return Response(template_name=self.template_name)
    
    @swagger_auto_schema(tags=["Authentication"])
    @csrf_exempt
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(
            {"success": True, "message": "Logged out"}, status=status.HTTP_200_OK
        )

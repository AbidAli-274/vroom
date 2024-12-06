from django.utils import timezone
from account.models import Member
from datetime import datetime
from inventory.models import BikeInventory,RentalLog,Addon
from inventory.serializers import BikeInventoryLimitedSerializer, BikeInventorySerializer,AddonSerializer,RentalLogSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.core.paginator import Paginator
import cloudinary
import cloudinary.uploader

class BikeInventoryVew(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'inventory/bike_inventory.html'

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the bike", type=openapi.TYPE_INTEGER),
            openapi.Parameter('class', openapi.IN_QUERY, description="Class of the bike", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Retrieve all Class xyz motorcycles & details",
                schema=BikeInventoryLimitedSerializer(many=True)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            bike_id = request.query_params.get('id')
            bike_class = request.query_params.get('class')
            
            filter_criteria = {}
            if bike_id:
                filter_criteria['id'] = bike_id
            if bike_class:
                filter_criteria['bike_class'] = bike_class
                
            queryset = BikeInventory.objects.filter(**filter_criteria) if filter_criteria else BikeInventory.objects.all().order_by('id')

            if request.accepted_renderer.format == 'html':
                paginator = Paginator(queryset, 18)  # Limit of 6 items per page
                page_number = request.query_params.get('page', 1)
                page_obj = paginator.get_page(page_number)

                return Response({
                    'bike_inventory': page_obj,
                }, template_name=self.template_name)

            serializer = BikeInventoryLimitedSerializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        request_body=BikeInventorySerializer,
        responses={
            200: openapi.Response(
                description="Add bike",
                schema=BikeInventorySerializer(many=True)
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            if data.get('photo'):
                img = data['photo']
            elif data.get('photo_url'):
                img = data['photo_url']
            else:
                img = None

            if img:
                cloudinary.config(
                    cloud_name = 'daj0lzvak',
                    api_key = '222713357542916',
                    api_secret = 'fyA1-yiKYPoL0ODKUWfqNse-D54',
                )
                cloudinary_img = cloudinary.uploader.upload(img,  use_filename = True)
                cloudinary_img_url = cloudinary_img['url']
                data['photo'] = cloudinary_img_url

            serializer = BikeInventorySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if request.accepted_renderer.format == 'html':
                    return JsonResponse(
                        {
                            "status": status.HTTP_200_OK,
                            "message": "Bike added successfully!",
                            "data": {
                                'bike': serializer.data
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        request_body=BikeInventorySerializer,
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the bike to update", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Bike updated successfully",
                schema=BikeInventorySerializer()
            ),
            400: openapi.Response(description="Invalid data or ID not provided"),
            404: openapi.Response(description="Bike not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            bike_id = request.query_params.get('id')
            if not bike_id:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                bike_id = int(bike_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            bike = BikeInventory.objects.filter(id=bike_id).first()
            if not bike:
                return Response({"error": "Bike not found"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data
            update_data = {}

            # Check each field to see if it's different from the existing value
            for field, value in data.items():
                if field == 'photo' and value:
                    # Delete the old photo if it exists
                    if bike.photo:
                        cloudinary.config(
                            cloud_name='daj0lzvak',
                            api_key='222713357542916',
                            api_secret='fyA1-yiKYPoL0ODKUWfqNse-D54',
                        )
                        # Extract public ID from the URL to delete the resource on Cloudinary
                        public_id = bike.photo.split('/')[-1].split('.')[0]
                        cloudinary.uploader.destroy(public_id)

                    # Upload the new photo to Cloudinary
                    cloudinary_img = cloudinary.uploader.upload(value, use_filename=True)
                    update_data['photo'] = cloudinary_img['url']
                elif field != 'photo' and hasattr(bike, field) and getattr(bike, field) != value:
                    update_data[field] = value

            if update_data:
                serializer = BikeInventorySerializer(bike, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Bike updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "No changes detected."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the Bike to delete", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Bike deleted successfully"),
            400: openapi.Response(description="ID must be provided"),
            404: openapi.Response(description="Bike not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            bike_id = request.query_params.get('id')

            if bike_id is None:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                bike_id = int(bike_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            bike = BikeInventory.objects.filter(id=bike_id).first()
            if bike is None:
                return Response({"error": "Bike not found"}, status=status.HTTP_404_NOT_FOUND)

            bike.delete()

            return Response({"success": "Bike deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RentalLogView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'inventory/rental_log.html'

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the bike to get all the rental dateTime", type=openapi.TYPE_INTEGER),
            openapi.Parameter('historical', openapi.IN_QUERY, description="Whether to include past records or not. (yes/no)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Get all rental dateTime for a chosen motorcycle",
                schema=RentalLogSerializer(many=True)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            bike_id = request.query_params.get('id')
            historical = request.query_params.get('historical')

            queryset = RentalLog.objects.all().order_by('id')

            if bike_id:
                queryset = queryset.filter(vehicle=bike_id)
            if historical:
                if historical.lower() == 'no':
                    queryset = queryset.filter(start_datetime__gte=timezone.now())
                elif historical.lower() == 'yes':
                    queryset = queryset
            
            records = [
                {
                    "id": rental.id,  
                    "records": [
                        {
                            "startDateTime": rental.start_datetime,
                            "endDateTime": rental.end_datetime
                        }
                    ]
                }
                for rental in queryset
            ]
            members = Member.objects.all()
            vehicles = BikeInventory.objects.all()
            addons = Addon.objects.all()

            if request.accepted_renderer.format == 'html':
                paginator = Paginator(queryset, 6)  # Limit of 6 items per page
                page_number = request.query_params.get('page', 1)
                page_obj = paginator.get_page(page_number)

                members = Member.objects.all()
                vehicles = BikeInventory.objects.all()
                addons = Addon.objects.all()


                return Response({
                    'rental_logs': page_obj,
                    'members': members,
                    'vehicles': vehicles,
                    'addons': addons
                }, template_name='inventory/rental_log.html')

            return Response(records)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

 
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'member': openapi.Schema(type=openapi.TYPE_INTEGER, description="Primary key of Member, e.g., 'recfViC2wT4Gk'"),
                'vehicle': openapi.Schema(type=openapi.TYPE_INTEGER, description="Primary key of BikeInventory, e.g., 'recGufwdq9FCy'"),
                'start_datetime': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description="Start date and time for the rental"),
                'end_datetime': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description="End date and time for the rental"),
                'addons': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description="List of addons by primary keys"), 
            },
            required=['member', 'vehicle', 'start_datetime', 'end_datetime'],
        ),
        responses={
            201: openapi.Response(
                description="Rental log created successfully",
                schema=RentalLogSerializer()
            ),
            400: "Bad Request",
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = RentalLogSerializer(data=data)
            if serializer.is_valid():
                rental_log = serializer.save()
                response_data = {
                    "id": rental_log.id,
                    "dailyDeposit": rental_log.vehicle.daily_deposit,
                    "monthlyDeposit": rental_log.vehicle.monthly_deposit,
                    "addonPrice": rental_log.price_deposit_addon - rental_log.price_deposit,
                    "rentalPrice": rental_log.rental_price,
                    "totalPrice": rental_log.price_deposit_addon
                }
                if request.accepted_renderer.format == 'html':
                    return JsonResponse(
                        {
                            "status": status.HTTP_200_OK,
                            "message": "Rental-log added successfully!",
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @swagger_auto_schema(
            request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'start_datetime': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description="Start date and time for the rental"),
                'end_datetime': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description="End date and time for the rental"),
                'addons': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description="List of addons by primary keys"), 
                'remarks': openapi.Schema(type=openapi.TYPE_STRING, description="Remarks"), 
                'paid': openapi.Schema(type=openapi.TYPE_STRING, description="paid (True/False)"), 
            },
        ),
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the rental-log to update", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Rental-log updated successfully",
                schema=RentalLogSerializer()
            ),
            400: openapi.Response(description="Invalid data or ID not provided"),
            404: openapi.Response(description="Rental-log not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            rental_log_id = request.query_params.get('id')
            if not rental_log_id:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                rental_log_id = int(rental_log_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            rental_log = RentalLog.objects.filter(id=rental_log_id).first()
            if not rental_log:
                return Response({"error": "Rental-log not found"}, status=status.HTTP_404_NOT_FOUND)

            data=request.data
            if data:
                # Pass the modified data to the serializer
                serializer = RentalLogSerializer(rental_log, data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Rental-log updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "No changes detected."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the rental-log to delete", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Rental-log deleted successfully"),
            400: openapi.Response(description="ID must be provided"),
            404: openapi.Response(description="Rental-log not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            rental_log_id = request.query_params.get('id')

            if rental_log_id is None:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Convert the ID to an integer
            try:
                rental_log_id = int(rental_log_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            rental_log = RentalLog.objects.filter(id=rental_log_id).first()
            if rental_log is None:
                return Response({"error": "Rental-log not found"}, status=status.HTTP_404_NOT_FOUND)

            rental_log.delete()

            return Response({"success": "Rental-log deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AddonView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'inventory/addon.html'

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Retrieve all Addons",
                schema=AddonSerializer(many=True)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = Addon.objects.all().order_by('id')

            if request.accepted_renderer.format == 'html':
                paginator = Paginator(queryset, 6)  
                page_number = request.query_params.get('page', 1)
                page_obj = paginator.get_page(page_number)
                return Response({'addons': page_obj}, template_name='inventory/addon.html')

            serializer = AddonSerializer(queryset, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        request_body=AddonSerializer,
        responses={
            200: openapi.Response(
                description="Crete addons",
                schema=AddonSerializer(many=True)
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = AddonSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if request.accepted_renderer.format == 'html':
                    return JsonResponse(
                            {
                                "status": status.HTTP_200_OK,
                                "message": "Addon added successfully!",

                            },
                            status=status.HTTP_200_OK,
                        )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        request_body=AddonSerializer,
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the addon to update", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Addon updated successfully",
                schema=AddonSerializer()
            ),
            400: openapi.Response(description="Invalid data or ID not provided"),
            404: openapi.Response(description="Addon not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            addon_id = request.query_params.get('id')
            if not addon_id:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                addon_id = int(addon_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            addon = Addon.objects.filter(id=addon_id).first()
            if not addon:
                return Response({"error": "Addon not found"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data
            if data:
                serializer = AddonSerializer(addon,data=data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Addon updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "No changes detected."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="ID of the Addon to delete", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Addon deleted successfully"),
            400: openapi.Response(description="ID must be provided"),
            404: openapi.Response(description="Addon not found"),
            500: openapi.Response(description="Internal server error"),
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            addon_id = request.query_params.get('id')

            if addon_id is None:
                return Response({"error": "ID must be provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                addon_id = int(addon_id)
            except ValueError:
                return Response({"error": "ID must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            addon = Addon.objects.filter(id=addon_id).first()
            if addon is None:
                return Response({"error": "Addon not found"}, status=status.HTTP_404_NOT_FOUND)

            addon.delete()

            return Response({"success": "Addon deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

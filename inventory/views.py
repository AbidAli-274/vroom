from django.utils import timezone
from account.models import Member
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
    permission_classes = [IsAuthenticated]
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
                paginator = Paginator(queryset, 6)  # Limit of 6 items per page
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
            data = request.data
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
            print(e)
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
            openapi.Parameter('historical', openapi.IN_QUERY, description="Whether to include past records or only records from now onwards (yes/no)", type=openapi.TYPE_STRING),
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
                queryset = queryset.filter(id=bike_id)
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
                'rental_days': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of rental days"),
                'addons': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description="List of addons by primary keys"), 
            },
            required=['member', 'vehicle', 'start_datetime', 'end_datetime', 'rental_days'],
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
        """
        Creates a rental log entry with the specified details.
        """
        try:
            data = request.data
            paid = data.get('paid', False)
            rental_days = int(data['rental_days']) 
            vehicle_id = data['vehicle']
            vehicle = BikeInventory.objects.get(id=vehicle_id)

            daily_rental = vehicle.daily_rental or 0
            weekly_rental = vehicle.weekly_rental or 0
            monthly_deposit = vehicle.monthly_deposit or 0
            daily_deposit = vehicle.daily_deposit or 0

            if rental_days < 3:
                rental_price = (daily_rental * rental_days) + 30
            elif 3 <= rental_days <= 6:
                rental_price = daily_rental * rental_days
            elif rental_days == 7:
                rental_price = weekly_rental
            else:
                complete_weeks = rental_days // 7
                leftover_days = rental_days % 7
                rental_price = (weekly_rental * complete_weeks) + (daily_rental * leftover_days)

            if rental_days >= 30:
                price_deposit = rental_price + monthly_deposit
            else:
                price_deposit = rental_price + daily_deposit

            addon_price = sum(Addon.objects.filter(id__in=data.get('addons', [])).values_list('rate', flat=True))
            price_deposit_addon = price_deposit + addon_price

            data['rental_price'] = rental_price
            data['price_deposit'] = price_deposit
            data['price_deposit_addon'] = price_deposit_addon
            data['paid']=paid

            serializer = RentalLogSerializer(data=data)
            if serializer.is_valid():
                rental_log = serializer.save()
                response_data = {
                    "id": rental_log.id,  # Assuming the primary key of RentalLog is 'id'
                    "dailyDeposit": daily_deposit,
                    "monthlyDeposit": monthly_deposit,
                    "addonPrice": addon_price,
                    "rentalPrice": rental_price,
                    "totalPrice": price_deposit_addon  # This should reflect the price deposit addon
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
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            queryset = Addon.objects.all()

            if request.accepted_renderer.format == 'html':
                return Response({'bike_inventory': queryset}, template_name='account/signup.html')

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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

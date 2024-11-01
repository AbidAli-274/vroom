from django.utils import timezone
from inventory.models import BikeInventory,RentalLog,Addon
from inventory.serializers import BikeInventoryLimitedSerializer, BikeInventorySerializer,AddonSerializer,RentalLogSerializer
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework import status


class BikeInventoryVew(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

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
                
            queryset = BikeInventory.objects.filter(**filter_criteria) if filter_criteria else BikeInventory.objects.all()

            if request.accepted_renderer.format == 'html':
                return Response({'bike_inventory': queryset}, template_name='inventory/bike_inventory.html')

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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RentalLogView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

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

            queryset = RentalLog.objects.all()
            if bike_id:
                queryset = queryset.filter(vehicle__id=bike_id)
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

            if request.accepted_renderer.format == 'html':
                return Response({'rental_logs': queryset}, template_name='inventory/rental_log.html')

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
            data['paid'] = False
            serializer = RentalLogSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class AddonView(APIView):
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

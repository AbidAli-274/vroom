from django.urls import path
from .views import BikeInventoryVew,RentalLogView,AddonView

urlpatterns = [
    path('bike/', BikeInventoryVew.as_view(), name='bike'),
    path('rental-log/', RentalLogView.as_view(), name='rental-log'),
    path('addon/', AddonView.as_view(), name='addon'),
]

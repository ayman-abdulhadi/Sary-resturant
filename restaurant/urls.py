from rest_framework.routers import DefaultRouter
from django.urls import path, include
from restaurant import views


app_name = 'restaurant'

router = DefaultRouter()

router.register('tables', views.TabletViewSet)
router.register('reservations', views.ReservationViewSet)


urlpatterns = [
    path('', include(router.urls))
]

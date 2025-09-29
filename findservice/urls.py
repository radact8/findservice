from django.urls import path
from . import views

urlpatterns = [
    path('',views.serviceList,name='sercielist'),
    path('service/<int:service_id>/', views.use_service, name='use_service'),
    path('service/1/<int:service_id>/', views.certificat_service, name='certificatService'),
    path('service/2/<int:service_id>/', views.education_service, name='educationService'),
    path('service/3/<int:service_id>/', views.elderly_service, name='ElderlyService'),
    path('service/4/<int:service_id>/', views.disabilities_service, name='disabilitiesService'),
    path('service/5/<int:service_id>/', views.health_service, name='healthService'),
    path('viewservice/certificat/',views.certificat_compatibility,name='certificatCompatibility'),
    # ルーティングの入り口となる use_service
    path('use_service/<int:service_id>/', views.use_service, name='use_service'),
]


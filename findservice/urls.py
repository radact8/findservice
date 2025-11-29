from django.urls import path
from . import views

urlpatterns = [
    path('',views.serviceList,name='sercielist'),
    path('service/<int:service_id>/', views.use_service, name='use_service'),
    path('service/1/<int:service_id>/', views.certificat_service, name='certificatService'),
    path('service/2/<int:service_id>/', views.education_service, name='educationService'),
    path('service/6/<int:service_id>/', views.welfareService, name='welfareService'),
    # ルーティングの入り口となる use_service
    path('use_service/<int:service_id>/', views.use_service, name='use_service'),
]


from django.contrib import admin
from .models import Service,certificatServicesConditions,viewCertificatServices,viewCertificatServicesMethod,kidsServicessConditions
# Register your models here.
# superuser username:admin pass:passadmin mailaddless: rrcf30@gmail.com
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(certificatServicesConditions)
class certificatServicesConditionsAdmin(admin.ModelAdmin):
    list_display = ['id','condition1','condition2','condition3','condition4']

@admin.register(viewCertificatServices)
class viewCertificatServicesAdmin(admin.ModelAdmin):
    list_display = ['id','serviceName','condition1','condition2','condition3','condition4']

@admin.register(viewCertificatServicesMethod)
class viewCertificatServicesMethodAdmin(admin.ModelAdmin):
    list_display = ['id','serviceName','cost','wardOfficePossible','wardOfficeDocument','conveniencePossible','convenienceDocument','mailPossible','mailDocument','supplement']

@admin.register(kidsServicessConditions)
class kidsServicessConditionsAdin(admin.ModelAdmin):
    list_display = ['serviceName','windows','mailAble','onlineAble','conditionAble','conditionLimit','conditionReference','conditionAdd']

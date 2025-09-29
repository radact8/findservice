from django.db import models

# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100)

class certificatServicesConditions(models.Model):
    # サービスとの紐付けが必要な場合は ForeignKey を追加
    # service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    
    # CharField から BooleanField に変更し、verbose_name に条件詳細を記述
    condition1 = models.BooleanField(default=False, verbose_name="足立区に住民登録がある")
    condition2 = models.BooleanField(default=False, verbose_name="足立区に印鑑登録している")
    condition3 = models.BooleanField(default=False, verbose_name="本籍が足立区にある")
    condition4 = models.BooleanField(default=False, verbose_name="今年度1月1日時点で足立区に住民登録")

    def __str__(self):
        return f"条件セット ({self.pk})" 

class viewCertificatServices(models.Model):
    serviceName = models.CharField(max_length=100)
    # CharField から BooleanField に変更し、verbose_name に条件詳細を記述
    condition1 = models.BooleanField(default=False, verbose_name="足立区に住民登録がある")
    condition2 = models.BooleanField(default=False, verbose_name="足立区に印鑑登録している")
    condition3 = models.BooleanField(default=False, verbose_name="本籍が足立区にある")
    condition4 = models.BooleanField(default=False, verbose_name="今年度1月1日時点で足立区に住民登録")

class viewCertificatServicesMethod(models.Model):
    serviceName = models.CharField(max_length=100)
    cost = models.CharField(max_length=100)
    wardOfficePossible= models.BooleanField(False)
    wardOfficeDocument = models.CharField(max_length=100)
    conveniencePossible = models.BooleanField(False)
    convenienceDocument = models.CharField(max_length=100)
    mailPossible = models.BooleanField(False)
    mailDocument = models.CharField(max_length=100)
    supplement = models.CharField(max_length=100,blank=True)

class kidsServicessConditions(models.Model):
    serviceName = models.CharField(max_length=100)
    windows = models.CharField(max_length=100)
    mailAble =  models.BooleanField(default=False)
    onlineAble = models.BooleanField(default=False)
    conditionAble = models.BooleanField(default=False,blank=True) #trueであり
    conditionLimit = models.IntegerField(blank=True,null=True)
    conditionReference = models.IntegerField(blank=True,null=True)
    conditionAdd = models.IntegerField(blank=True,null=True)
    
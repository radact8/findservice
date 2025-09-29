from django.db import models
import uuid

# Create your models here.

class Page(models.Model):
    id = models.UUIDField(
        primary_key = True,default=uuid.uuid4,editable=False,verbose_name="ID")
    title = models.CharField(max_length=100,verbose_name="タイトル")
    body = models.TextField(max_length=2000,verbose_name="本文")
    page_date = models.DateField(verbose_name="日付")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(auto_now=True,verbose_name="更新日時")

    def __str__(self):
        return self.title
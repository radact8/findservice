from django.contrib import admin
from .models import Page

# Register your models here.
# superuser username:admin pass:passadmin mailaddless: rrcf30@gmail.com
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    readonly_fields = ["id","created_at","update_at"]
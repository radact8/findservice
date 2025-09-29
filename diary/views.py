from django.shortcuts import render,redirect
from django.views import View
from .forms import PageForm
from .models import Page
from datetime import datetime
from zoneinfo import ZoneInfo

# Create your views here.
class IndexView(View):
    def get(self,request):
        datetime_now = datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).strftime("%Y年%m月%d日 %H:%M:%S")
        return render(request,"diary/index.html",{"datetime_now": datetime_now})

class PageCreateView(View):
    def get(self,request):
        form = PageForm()
        return render(request,"diary/page_form.html",{"form": form})

    def post(self,request):
        form = PageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("diary:index")

class PageListView(View):
    def get(slef,request):
        page_list = Page.objects.all()
        return render(request,"diary/page_list.html",{"page_list":page_list})

index = IndexView.as_view()
page_create =  PageCreateView.as_view()
page_list = PageListView.as_view()
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Service,certificatServicesConditions,viewCertificatServices,viewCertificatServicesMethod
from .forms import ConditionSelectionForm
# Create your views here.
def serviceList(request):
    services = Service.objects.all()
    return render(request,'findservice/serviceList.html', {'services': services})

def use_service(request, service_id):
    if service_id == 1:
        return redirect('certificatService', service_id=service_id) #証明書発行
    elif service_id == 2:
        return redirect('educationService', service_id=service_id) #子育て・教育
    elif service_id == 3: 
        return redirect('ElderlyService', service_id=service_id) #高齢者福祉
    elif service_id == 4:
        return redirect('disabilitiesService', service_id=service_id) #障碍者福祉
    elif service_id == 5:
        return redirect('healthService', service_id=service_id) #健康・医療
    else:
        return HttpResponseNotFound("サービスが見つかりません")

# 各サービスのビュー

def certificat_service(request, service_id): #証明書発行
    """
    条件選択フォームを表示し、POSTデータを受け付けて処理するビュー。
    """
    
    # HTTPメソッドがPOSTかどうかをチェック
    if request.method == 'POST':
        # POSTデータを使ってフォームをインスタンス化（データバインディング）
        form = ConditionSelectionForm(request.POST)
        
        # フォームのデータが有効か検証
        if form.is_valid():
            # is_valid()がTrueの場合、データはPythonのTrue/Falseに変換済み
            
            # データベースに新しいレコードとして保存条件
            # commit=True (デフォルト) なので、ここでDBに保存される
            #condition_set = form.save() 
            user_conditions = form.cleaned_data
            
            # 【重要】データをセッションに保存
            # セッションキーはユニークな名前に設定
            request.session['certificat_user_conditions'] = user_conditions
            return redirect('certificatCompatibility')
            
            # 処理完了後、確認ページなどにリダイレクトするのが一般的
            # return redirect('success_page') 

    else:
        # GETリクエストの場合、空のフォームをインスタンス化して表示
        form = ConditionSelectionForm()

    # テンプレートにフォームを渡してレンダリング
    context = {
        'form': form
    }
    return render(request, 'findservice/certificat_service.html',context)

def education_service(request, service_id): #子育て・教育
    return render(request, 'services/education_service.html', {'service_id': service_id})

def elderly_service(request, service_id): # 高齢者福祉
    return render(request, 'services/elderly_service.html', {'service_id': service_id})

def disabilities_service(request, service_id): # 障碍者福祉
    return render(request, 'services/disabilities_service.html', {'service_id': service_id})

def health_service(request, service_id): #健康・医療
    return render(request, 'services/health_service.html', {'service_id': service_id})


def certificat_compatibility(request):
    user_conditions = request.session.get('certificat_user_conditions')
    check_condions = viewCertificatServices.objects.all()
    getAbleSercvice = list(viewCertificatServicesMethod.objects.all())
    check_list = list(check_condions)
    ableSercvice = []
    for i in range(len(check_list)):
        for j in range(len(user_conditions)):
            condition_field_name = f'condition{j+1}' 
            # 2. getattr(オブジェクト, 属性名[文字列]) を使って値を取得する
            #    例: j=1 のとき、getattr(check_list[i], 'condition1') を実行
            if getattr(check_list[i], condition_field_name) is True:
                # ... True だった場合の処理 ...
                if(user_conditions[condition_field_name] == True):
                    ableSercvice.append(getAbleSercvice[i])

        
    #print(check_list[0].condition1)
    #print(user_conditions['condition1'])
    #print(len(check_list))
    print(ableSercvice)
    return render(request,'findservice/certificat_compatibility.html',{'ableSercvice':ableSercvice})
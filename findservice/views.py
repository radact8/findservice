from django.shortcuts import render,redirect
from .logic import WelfareCalculator
from django.http import HttpResponse
from .models import Service,certificatServicesConditions,viewCertificatServices,viewCertificatServicesMethod
from .forms import ConditionSelectionForm,EligibilityForm
from django.http import HttpResponseNotFound
# Create your views here.
def serviceList(request):
    services = Service.objects.all()
    return render(request,'findservice/serviceList.html', {'services': services})

def use_service(request, service_id):
    if service_id == 1:
        return redirect('certificatService', service_id=service_id) #証明書発行
    elif service_id == 2:
        return redirect('educationService', service_id=service_id) #子育て・教育
    elif service_id == 6: 
        return redirect('welfareService', service_id=service_id) #高齢者福祉
    else:
        return ("サービスが見つかりません")

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
            request.session['education_service_user_conditions'] = user_conditions
            return redirect('education_serviceComspatibility')
            
            # 処理完了後、確認ページなどにリダイレクトするのが一般的
            # return redirect('success_page') 

    else:
        # GETリクエストの場合、空のフォームをインスタンス化して表示
        form = ConditionSelectionForm()

    # テンプレートにフォームを渡してレンダリング
    context = {
        'form': form
    }
    return render(request, 'findservice/education_service.html',context)


def certificat_compatibility(request,service_id):
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

def welfareService(request,service_id):
    result = None
    
    if request.method == 'POST':
        form = EligibilityForm(request.POST)
        if form.is_valid():
            # バリデーション済みのデータを取得
            data = form.cleaned_data
            
            # ロジッククラスを呼び出し
            calculator = WelfareCalculator()
            result = calculator.calculate(data)
            
            # ここでDB保存（Model.save）は一切行いません
    else:
        form = EligibilityForm()

    context = {
        'form': form,
        'result': result,
    }
    
    # 入力画面と結果を同一ページ、あるいは結果ページへレンダリング
    return render(request, 'findservice/welfare_service.html', context)
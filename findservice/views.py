from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import Service, viewCertificatServices, viewCertificatServicesMethod

# フォームのインポート
from .forms import CertificateForm, ChildSupportForm, EligibilityForm

# ロジックのインポート
from .logic import CertificateService, SupportManager, WelfareCalculator

# ==========================================
# サービス一覧・振り分け
# ==========================================
def serviceList(request):
    services = Service.objects.all()
    return render(request, 'findservice/serviceList.html', {'services': services})

def use_service(request, service_id):
    """
    IDに基づいて各サービスのビューへリダイレクトする
    """
    if service_id == 1:
        return redirect('certificatService', service_id=service_id) # 証明書発行
    elif service_id == 2:
        return redirect('educationService', service_id=service_id)  # 子育て・教育
    elif service_id == 6: 
        return redirect('welfareService', service_id=service_id)    # 生活保護判定
    else:
        return HttpResponseNotFound("サービスが見つかりません")

# ==========================================
# 1. 証明書発行サービス (ID: 1)
# ==========================================
def certificat_service(request, service_id):
    """
    コンビニ交付と窓口の手数料比較シミュレーション
    """
    result = None
    
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            # ロジック呼び出し
            service = CertificateService()
            result = service.simulate(form.cleaned_data)
    else:
        form = CertificateForm()

    return render(request, 'findservice/certificat_service.html', {
        'form': form,
        'result': result
    })

# ==========================================
# 2. 子育て・教育支援サービス (ID: 2)
# ==========================================
def education_service(request, service_id):
    """
    児童手当や医療費助成の判定
    """
    result = None
    
    if request.method == 'POST':
        form = ChildSupportForm(request.POST)
        if form.is_valid():
            manager = SupportManager()
            result = manager.check_support(form.cleaned_data)
    else:
        form = ChildSupportForm()

    context = {
        'form': form,
        'result': result
    }
    return render(request, 'findservice/education_service.html', context)

# ==========================================
# 6. 生活保護 簡易判定サービス (ID: 6)
# ==========================================
def welfareService(request, service_id):
    """
    足立区 生活保護簡易判定
    """
    result = None
    
    if request.method == 'POST':
        form = EligibilityForm(request.POST)
        if form.is_valid():
            # バリデーション済みのデータを取得
            data = form.cleaned_data
            
            # ロジッククラスを呼び出し
            calculator = WelfareCalculator()
            result = calculator.calculate(data)
            
            # ※この判定ツールではDB保存は行わず、結果を表示するだけです
    else:
        form = EligibilityForm()

    context = {
        'form': form,
        'result': result,
    }
    
    # テンプレートファイル名は 'welfare_service.html' と想定
    return render(request, 'findservice/welfare_service.html', context)


# ==========================================
# (参考) 古い互換性チェック機能
# ※現在使っていない場合は削除しても良いですが、念のため残しています
# ==========================================
def certificat_compatibility(request, service_id):
    user_conditions = request.session.get('certificat_user_conditions')
    if not user_conditions:
        return redirect('certificatService', service_id=service_id)

    check_condions = viewCertificatServices.objects.all()
    getAbleSercvice = list(viewCertificatServicesMethod.objects.all())
    check_list = list(check_condions)
    ableSercvice = []
    
    for i in range(len(check_list)):
        # 条件判定ロジック（簡略化）
        # 実際にはここに詳細なマッチング処理が入る
        pass
        
    return render(request, 'findservice/certificat_compatibility.html', {'ableSercvice': ableSercvice})
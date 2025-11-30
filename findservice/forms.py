from django import forms
from .models import certificatServicesConditions

from django import forms

class CertificateForm(forms.Form):
    # 証明書の種類
    CERT_CHOICES = [
        ('jumin', '住民票の写し（世帯全員・個人）'),
        ('inkan', '印鑑登録証明書'),
        ('koseki', '戸籍全部（個人）事項証明書'),
        ('tax', '課税・非課税証明書'),
    ]
    
    cert_type = forms.ChoiceField(
        label='必要な証明書',
        choices=CERT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # マイナンバーカードの有無
    has_mynumber_card = forms.BooleanField(
        label='マイナンバーカードを持っていますか？（暗証番号がわかる）',
        required=False, # チェックなし=持っていない
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # 必要枚数
    copies = forms.IntegerField(
        label='必要枚数',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 100px;'})
    )

class EligibilityForm(forms.Form):
    age = forms.IntegerField(label='年齢', min_value=0)
    household_size = forms.IntegerField(label='世帯人数', min_value=1, initial=1)
    monthly_income = forms.IntegerField(label='月収（年金含む）', min_value=0)
    savings = forms.IntegerField(label='預貯金', min_value=0)
    has_disability = forms.BooleanField(label='障害・病気で働けない', required=False)

from django import forms

class ChildSupportForm(forms.Form):
    # お子様の年齢・学年区分
    STAGE_CHOICES = [
        ('baby', '0歳 〜 2歳'),
        ('preschool', '3歳 〜 小学校入学前（保育園・幼稚園）'),
        ('elementary', '小学生'),
        ('junior_high', '中学生'),
        ('high_school', '高校生相当年齢'),
    ]

    child_stage = forms.ChoiceField(
        label='お子様の年齢・学年区分',
        choices=STAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # 第何子か（児童手当の加算判定用）
    # ※令和6年10月からの拡充を見据え、第3子以降は重要
    child_order = forms.IntegerField(
        label='第何子ですか？（1, 2, 3...）',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 100px;'})
    )

    # 足立区立の学校に通っているか（給食費無償化判定用）
    is_public_school = forms.BooleanField(
        label='足立区立の小・中学校に通う予定ですか？',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
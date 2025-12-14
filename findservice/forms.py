from django import forms

# ==========================================
# 1. コンビニ交付・証明書発行シミュレーション用
# ==========================================
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

# ==========================================
# 2. 生活保護 簡易判定用（大幅アップデート版）
# ==========================================
class EligibilityForm(forms.Form):
    # --- 基本属性 ---
    age = forms.IntegerField(
        label='世帯主の年齢',
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 35'})
    )

    # --- 世帯構成（判定精度のカギ） ---
    household_size = forms.IntegerField(
        label='世帯人数（あなたを含む全員）',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='※家賃の上限額判定に使用します'
    )

    num_children = forms.IntegerField(
        label='そのうち18歳以下の子供の人数',
        min_value=0,
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='※児童養育加算の判定に使用します'
    )

    is_single_parent = forms.BooleanField(
        label='ひとり親世帯ですか？',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='※母子加算・父子加算の判定に使用します'
    )

    # --- 経済状況 ---
    # logic.pyに合わせて 'income' に統一
    income = forms.IntegerField(
        label='世帯の月収（給与・年金・手当など）',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 120000'}),
        help_text='※手取りではなく総支給額の目安を入力してください'
    )

    rent = forms.IntegerField(
        label='現在の家賃（管理費・共益費は除く）',
        min_value=0,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 53000'}),
        help_text='※持ち家の場合は0円'
    )

    savings = forms.IntegerField(
        label='世帯全員の預貯金・現金合計',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '例: 50000'})
    )

    has_asset = forms.BooleanField(
        label='処分価値のある資産（車・バイク・不動産）を持っていますか？',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='※生活に必須でない資産は処分の対象となります'
    )

    # --- 健康状態（統合版） ---
    disability_level = forms.ChoiceField(
        label='健康状態・障害の有無',
        choices=[
            ('healthy', '健康 / 働ける'),
            ('sick_no_cert', '病気・ケガで療養中（手帳なし）'),
            ('grade3', '障害者手帳 3級'),
            ('grade12', '障害者手帳 1・2級（または障害年金1・2級）'),
        ],
        initial='healthy',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='※障害者加算の判定に使用します'
    )

# ==========================================
# 3. 子育て・教育支援 シミュレーション用
# ==========================================
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
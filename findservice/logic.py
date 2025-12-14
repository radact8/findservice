# logic.py
import datetime

class WelfareCalculator:
    """
    生活保護 簡易判定ロジック（足立区・令和6年度基準ベース）
    """
    # --- 定数定義 ---

    # 足立区（1級地-1）の家賃上限テーブル（世帯人数ごと）
    # ソース: 足立区「生活保護のしおり」等
    RENT_CAP_TABLE = {
        1: 53700,
        2: 64000,
        3: 69800,
        4: 69800,
        5: 69800,
        # 6人以上は本来もっと増えますが、一旦最大値を設定
        6: 75000 
    }

    # 生活扶助基準（第1類+第2類）の概算
    BASE_COST_ADULT = 78000  # 若年単身
    BASE_COST_ELDER = 74000  # 高齢単身
    
    # 子供の生活扶助概算（年齢で細かく違いますが平均値を採用）
    COST_PER_CHILD = 45000 

    # 各種加算（月額）
    ADDITION_WINTER = 2630            # 冬季加算（11-3月）×人数
    ADDITION_SINGLE_PARENT = 21000    # 母子・父子加算（平均値）
    ADDITION_CHILD_REARING = 10000    # 児童養育加算（子供1人あたり）
    
    ADDITION_DISABILITY_G12 = 26810   # 障害者加算 1・2級
    ADDITION_DISABILITY_G3 = 17870    # 障害者加算 3級（※要件ありだが簡易判定として採用）

    def calculate(self, data):
        # データの取得
        age = data.get('age', 30)
        rent = data.get('rent', 0)
        income = data.get('income', 0)
        savings = data.get('savings', 0)
        has_asset = data.get('has_asset', False)
        
        # 世帯情報の取得（今回追加分）
        household_size = data.get('household_size', 1)
        num_children = data.get('num_children', 0)
        is_single_parent = data.get('is_single_parent', False)
        
        disability_level = data.get('disability_level', 'healthy')

        # --- 1. 最低生活費の算出 ---
        
        # (A) 生活扶助本体（食費・光熱費など）
        # 世帯主
        living_cost = self.BASE_COST_ELDER if age >= 65 else self.BASE_COST_ADULT
        
        # 子供・その他家族分を加算（簡易計算：大人1名以外を子供または同居人として計算）
        # ※本来は逓減率がありますが、シミュレーターとしては人数×単価で近似
        others_count = max(0, household_size - 1)
        living_cost += (others_count * self.COST_PER_CHILD)

        # (B) 加算の計算
        
        # 母子・父子加算（ひとり親の場合）
        if is_single_parent and num_children > 0:
            living_cost += self.ADDITION_SINGLE_PARENT

        # 児童養育加算（子供の人数分）
        if num_children > 0:
            living_cost += (num_children * self.ADDITION_CHILD_REARING)

        # 障害者加算
        if disability_level == 'grade12':
            living_cost += self.ADDITION_DISABILITY_G12
        elif disability_level == 'grade3':
            living_cost += self.ADDITION_DISABILITY_G3

        # 冬季加算（11月〜3月）※世帯人数分つく
        current_month = datetime.date.today().month
        if current_month in [11, 12, 1, 2, 3]:
            living_cost += (self.ADDITION_WINTER * household_size)

        # (C) 住宅扶助（家賃）
        # 世帯人数に応じた上限を取得（6人以上は6として扱う）
        cap_key = min(household_size, 6)
        rent_cap = self.RENT_CAP_TABLE.get(cap_key, 53700)
        
        actual_housing_aid = min(rent, rent_cap)

        # ★最低生活費（判定ライン）
        minimum_cost = int(living_cost + actual_housing_aid)

        # --- 2. 収入認定（勤労控除） ---
        deduction = 0
        if income > 0:
            # 基礎控除の簡易計算
            if income < 15200:
                deduction = income
            else:
                deduction = 15000 + (income * 0.1) # 簡易ロジック

        recognized_income = max(0, income - deduction)

        # --- 3. 判定結果 ---
        
        # 資産チェック
        allowed_savings = minimum_cost * 0.5
        if has_asset or savings > allowed_savings:
            return {
                'is_eligible': False,
                'message': '資産（車・多額の預貯金）があるため、まずはそちらの活用が優先されます。'
            }

        gap = minimum_cost - recognized_income

        if gap > 0:
            return {
                'is_eligible': True,
                'amount': int(gap),
                'minimum_cost': minimum_cost,
                'message': '受給対象となる可能性があります。'
            }
        else:
            return {
                'is_eligible': False,
                'excess': int(abs(gap)),
                'minimum_cost': minimum_cost,
                'message': '収入が基準を上回っています。'
            }


class SupportManager:
    """
    子育て・教育支援の判定ロジック
    """
    def check_support(self, data):
        stage = data['child_stage']
        order = data['child_order'] 
        is_public = data['is_public_school']

        supports = []
        total_monthly_benefit = 0

        # --- 1. 児童手当（国制度・R6.10改正版） ---
        allowance = 0
        if stage in ['baby', 'preschool', 'elementary', 'junior_high', 'high_school']:
            # 第3子以降は3万円
            if order >= 3:
                allowance = 30000
            else:
                # 0-2歳は1.5万、3歳〜高校生は1万
                if stage == 'baby':
                    allowance = 15000
                else:
                    allowance = 10000
            
            supports.append({
                'name': '児童手当',
                'amount': f'月額 {allowance:,} 円',
                'desc': '令和6年10月より所得制限撤廃・高校生年代まで延長・第3子加算拡充。'
            })
            total_monthly_benefit += allowance

        # --- 2. 東京都 018サポート ---
        if stage in ['baby', 'preschool', 'elementary', 'junior_high', 'high_school']:
            supports.append({
                'name': '東京都 018サポート',
                'amount': '月額 5,000 円',
                'desc': '都内在住の0〜18歳全員に支給（所得制限なし）。'
            })
            total_monthly_benefit += 5000

        # --- 3. 医療費助成（マル乳・マル子・マル青） ---
        medical_name = ''
        if stage in ['baby', 'preschool']:
            medical_name = 'マル乳（乳幼児医療費助成）'
        elif stage in ['elementary', 'junior_high']:
            medical_name = 'マル子（子ども医療費助成）'
        elif stage == 'high_school':
            medical_name = 'マル青（高校生等医療費助成）'
        
        if medical_name:
            supports.append({
                'name': medical_name,
                'amount': '医療費 0 円',
                'desc': '通院・入院ともに自己負担なし（足立区・東京都）。'
            })

        # --- 4. 【追加】高校授業料の実質無償化（東京都） ---
        if stage == 'high_school':
            supports.append({
                'name': '高校授業料の実質無償化',
                'amount': '年額 約47.5万円まで助成',
                'desc': '【重要】東京都では私立・公立問わず、所得制限なしで授業料が実質無償化されています（授業料軽減助成金）。'
            })

        # --- 5. 給食費無償化（足立区） ---
        if is_public and stage == 'elementary':
            supports.append({
                'name': '小学校給食費無償化',
                'amount': '全額免除',
                'desc': '足立区立小学校の給食費は区が全額負担します。'
            })
        elif is_public and stage == 'junior_high':
            supports.append({
                'name': '中学校給食費無償化',
                'amount': '全額免除',
                'desc': '足立区立中学校の給食費は区が全額負担します。'
            })

        # --- 6. 幼児教育・保育の無償化 ---
        if stage == 'preschool':
             supports.append({
                'name': '幼児教育・保育の無償化',
                'amount': '利用料 0 円（上限あり）',
                'desc': '認可保育所等は無料。幼稚園等は月額2.57万円まで無償。'
            })

        return {
            'stage_display': dict(forms.ChildSupportForm.STAGE_CHOICES).get(stage),
            'supports': supports,
            'total_cash': total_monthly_benefit
        }

class CertificateService:
    # ... (既存のCERT_DATA設定) ...
    # 省略（元のコードのままでOKですが、simluateメソッドの最後の注意書きだけ修正します）

    def simulate(self, data):
        # ... (前半のロジックは同じ) ...
        
        # 注意書きの追加
        maintenance_msg = '\n※年末年始（12/29〜1/3）やメンテナンス日はコンビニ交付を利用できません。'
        
        if result['message']:
            result['message'] += maintenance_msg
        else:
             result['message'] = maintenance_msg.strip()
             
        return result
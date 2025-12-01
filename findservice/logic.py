import datetime
from .forms import ChildSupportForm

class WelfareCalculator:
    # 足立区（1級地-1）の家賃上限（単身）
    HOUSING_CAP = 53700
    
    # 年齢別の生活扶助基準（第1類+第2類） ※令和5-6年度基準の概算
    # 実際はより細かいですが、アプリ用として代表値を設定
    BASE_COST_YOUNG = 85120  # 20〜40歳くらい
    BASE_COST_ELDER = 78000  # 65歳以上くらい

    # 冬季加算（11月〜3月）
    WINTER_ADDITION = 2630 

    def calculate(self, data):
        age = data['age']
        rent = data['rent']
        income = data['income']
        savings = data['savings']
        has_asset = data['has_asset']

        # --- 基準額の決定 ---
        # 年齢によるベース金額の切り替え
        if age >= 65:
            base_living_cost = self.BASE_COST_ELDER
        else:
            base_living_cost = self.BASE_COST_YOUNG
        
        # 冬季加算の判定（現在の月を取得）
        current_month = datetime.date.today().month
        # 11, 12, 1, 2, 3月なら加算
        if current_month in [11, 12, 1, 2, 3]:
            base_living_cost += self.WINTER_ADDITION

        # 家賃（実費と上限の低い方）
        actual_housing_aid = min(rent, self.HOUSING_CAP)

        # ★最低生活費（ボーダーライン）
        minimum_cost = base_living_cost + actual_housing_aid

        # --- 判定 ---
        # 門前払いフィルタ（資産）
        if has_asset or savings > (minimum_cost * 0.5):
            return {
                'is_eligible': False,
                'message': '資産（車・多額の預貯金）があるため、まずはそちらを活用してください。'
            }

        gap = minimum_cost - income

        if gap > 0:
            return {
                'is_eligible': True,
                'amount': gap,
                'minimum_cost': minimum_cost,
                'message': '受給対象となる可能性があります。'
            }
        else:
            return {
                'is_eligible': False,
                'excess': abs(gap),
                'minimum_cost': minimum_cost,
                'message': '収入が基準を上回っています。'
            }
        

class CertificateService:
    # 証明書ごとの設定（名称、窓口料金、コンビニ料金、コンビニ利用可否）
    # ※足立区のコンビニ交付は通常、窓口より100円程度安い設定になっています
    CERT_DATA = {
        'jumin': {
            'name': '住民票の写し',
            'fee_window': 300,
            'fee_konbini': 200,
            'konbini_available': True
        },
        'inkan': {
            'name': '印鑑登録証明書',
            'fee_window': 300,
            'fee_konbini': 200,
            'konbini_available': True
        },
        'koseki': {
            'name': '戸籍全部（個人）事項証明書',
            'fee_window': 450,
            'fee_konbini': 450, # 戸籍は同額の場合が多いが区により異なる（足立区は同額または低減）
            'konbini_available': True
        },
        'tax': {
            'name': '課税・非課税証明書',
            'fee_window': 300,
            'fee_konbini': 200,
            'konbini_available': True
        }
    }

    def simulate(self, data):
        """
        フォームデータを受け取り、最適な取得方法と料金を返す
        """
        cert_type = data['cert_type']
        has_card = data['has_mynumber_card']
        copies = data['copies']

        # 選択された証明書のデータ取得
        info = self.CERT_DATA.get(cert_type)
        if not info:
            return None

        result = {
            'name': info['name'],
            'copies': copies,
            'recommendation': '',
            'total_fee': 0,
            'places': []
        }

        # --- 判定ロジック ---
        
        # パターンA: マイナンバーカードがあり、コンビニ交付対応の証明書の場合
        if has_card and info['konbini_available']:
            unit_price = info['fee_konbini']
            total = unit_price * copies
            
            result['recommendation'] = 'コンビニ交付がおすすめです！'
            result['is_konbini'] = True
            result['unit_price'] = unit_price
            result['total_fee'] = total
            result['places'] = ['セブンイレブン', 'ローソン', 'ファミリーマート', 'ミニストップ']
            result['message'] = (
                f'窓口よりも待ち時間が少なく、手数料もお得（または同額）です。\n'
                f'マルチコピー機で「行政サービス」を選択してください。'
            )

        # パターンB: カードがない、またはコンビニ非対応の場合 -> 窓口案内
        else:
            unit_price = info['fee_window']
            total = unit_price * copies
            
            result['recommendation'] = '区役所・区民事務所の窓口へお越しください'
            result['is_konbini'] = False
            result['unit_price'] = unit_price
            result['total_fee'] = total
            result['places'] = ['足立区役所（本庁）', '各区民事務所（千住、綾瀬など）']
            
            if has_card and not info['konbini_available']:
                result['message'] = 'この証明書はマイナンバーカードがあってもコンビニでは発行できません。'
            elif not has_card:
                result['message'] = 'マイナンバーカードをお持ちでないため、窓口での交付となります。'
                # 印鑑証明の場合の注意喚起
                if cert_type == 'inkan':
                    result['message'] += '\n※「印鑑登録証（カード）」を必ずご持参ください。'
                # 住民票などの場合
                else:
                    result['message'] += '\n※本人確認書類（免許証など）をご持参ください。'

        return result
    
class SupportManager:
    def check_support(self, data):
        stage = data['child_stage']
        order = data['child_order'] # 第何子か
        is_public = data['is_public_school']

        supports = []
        total_monthly_benefit = 0

        # --- 1. 児童手当（国制度） ---
        # ※令和6年10月改正後のルール（所得制限なし、高校生まで、第3子加算増）を適用
        allowance_amount = 0
        
        if stage in ['baby', 'preschool', 'elementary', 'junior_high', 'high_school']:
            # 第3子以降は一律3万円
            if order >= 3:
                allowance_amount = 30000
            else:
                # 第1・2子
                if stage == 'baby': # 0-2歳
                    allowance_amount = 15000
                elif stage in ['preschool', 'elementary', 'junior_high', 'high_school']:
                    allowance_amount = 10000
            
            supports.append({
                'name': '児童手当',
                'amount': f'月額 {allowance_amount:,} 円',
                'desc': '令和6年10月より所得制限撤廃・高校生年代まで延長されています。'
            })
            total_monthly_benefit += allowance_amount

        # --- 2. 018サポート（東京都独自） ---
        # 都内在住の0-18歳に月額5000円
        if stage in ['baby', 'preschool', 'elementary', 'junior_high', 'high_school']:
            supports.append({
                'name': '東京都 018サポート',
                'amount': '月額 5,000 円',
                'desc': '東京都独自の支援策です（所得制限なし）。'
            })
            total_monthly_benefit += 5000

        # --- 3. 子ども医療費助成（マル乳・マル子・マル青） ---
        # 足立区は高校生相当年齢まで医療費助成あり（所得制限なし）
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
                'amount': '自己負担 0 円',
                'desc': '通院・入院ともに医療費（保険診療分）が無料になります。'
            })

        # --- 4. 学校給食費無償化（足立区独自） ---
        if is_public and stage == 'elementary':
            supports.append({
                'name': '小学校給食費無償化',
                'amount': '全額補助',
                'desc': '足立区立小学校の給食費は区が全額負担します（年間約5万円相当の支援）。'
            })
        elif is_public and stage == 'junior_high':
            supports.append({
                'name': '中学校給食費無償化',
                'amount': '全額補助',
                'desc': '足立区立中学校の給食費は区が全額負担します（年間約6万円相当の支援）。'
            })

        # --- 5. 幼児教育・保育の無償化 ---
        if stage == 'preschool':
             supports.append({
                'name': '幼児教育・保育の無償化',
                'amount': '利用料 0 円（上限あり）',
                'desc': '認可保育所等は無料。幼稚園等は月額2.57万円まで無償。'
            })

        return {
            'stage_display': dict(ChildSupportForm.STAGE_CHOICES).get(stage),
            'supports': supports,
            'total_cash': total_monthly_benefit
        }
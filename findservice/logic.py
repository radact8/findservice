import datetime

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
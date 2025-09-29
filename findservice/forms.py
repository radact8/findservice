from django import forms
from .models import certificatServicesConditions

class ConditionSelectionForm(forms.ModelForm):
    class Meta:
        model = certificatServicesConditions
        # serviceフィールドは管理用なので除外
        exclude = ('service',) 
        # fields = '__all__' # 全てのフィールドを含める場合
        
    def clean(self):
        # フォームのバリデーションロジックをここに追加できます
        cleaned_data = super().clean()
        
        # 例: 住民登録がないのに印鑑登録があることは矛盾するので、チェックを入れる。
        if cleaned_data.get('is_seal_registered') and not cleaned_data.get('is_adachi_resident'):
            raise forms.ValidationError(
                "印鑑登録をするには住民登録が必要です。選択内容を確認してください。"
            )
        return cleaned_data 
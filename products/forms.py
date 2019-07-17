from products.models import CoaFile, ProductGroup
from django import forms
class CoaFileForm(forms.ModelForm):
    
    class Meta:
        model = CoaFile
        fields = ("file",)

class ProductGroupForm(forms.ModelForm):

    class Meta:
        model = ProductGroup
        fields = ("name",)
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'post-text',
                'required': True,
            }),
        }
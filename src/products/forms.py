from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductAttachment


input_css_class = "form-control"
# input_css_class = "bg-neutral-secondary-medium border border-default-medium text-heading text-sm rounded-base focus:ring-brand focus:border-brand block w-full px-3 py-2.5 shadow-xs placeholder:text-body"
class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ["name","handle","price"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['name'].widget.attrs['placeholder'] = "Your Name"
        for field in self.fields:
            self.fields[field].widget.attrs ['class'] =  input_css_class        


class ProductUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ["image", "name","handle","price"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['name'].widget.attrs['placeholder'] = "Your Name"
        for field in self.fields:
            self.fields[field].widget.attrs ['class'] =  input_css_class        

class ProductAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProductAttachment
        fields = ['file', 'name', 'is_free', 'active']
        labels = {
            'file': 'Attachment file',
            'name': 'Attachment name',
            'is_free': 'Free download',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['is_free', 'active']:
                self.fields[field].widget.attrs['class'] = input_css_class

ProductAttachmentInlineFormSet = inlineformset_factory(
    Product, 
    ProductAttachment,
    form=ProductAttachmentForm,
    extra=0,
    can_delete=True,
)

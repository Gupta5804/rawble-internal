#from django import forms
#from django.forms import ModelForm
#from django.forms.models import inlineformset_factory
#from contacts.models import ContactVendor
#from deals.models import DealBuyer,DealBuyerProduct,DealVendor,DealVendorProduct
#from django.contrib.admin import widgets
#from products.models import Product
#class DealBuyerCreateForm(ModelForm):
    
#    class Meta:
#        model = DealBuyer
        #fields = ['date']
#        exclude = ['relationship_manager','created_by','payment_terms']
        

#class DealVendorCreateForm(ModelForm):
#    
#    class Meta:
#        model = DealVendor
#        #fields = ['date']
#        exclude = ['relationship_manager','created_by','payment_terms']


#DealBuyerProductFormSet = inlineformset_factory(DealBuyer,DealBuyerProduct,exclude=['make','unit']) 
#DealVendorProductFormSet = inlineformset_factory(DealVendor,DealVendorProduct,exclude=['make','unit'])

#class VendorDealForm1(forms.Form):
#    vendors = ContactVendor.objects.all()
#    vendor_choice_list =[]
#    for vendor in vendors:
#        vendor_choice_list.append((vendor.contact_id,vendor.contact_name))
#
#    delivery_terms_choices =[('Door Delivery','Door Delivery'),('Ex-Godown','Ex-Godown'),('FOR','FOR'),('Local Transport','Local Transport')]
#    vendor = forms.ChoiceField(choices=vendor_choice_list,label = "Select Vendor")
#    delivery_terms = forms.ChoiceField(choices = delivery_terms_choices , label="Select Delivery Term")
#class VendorDealForm2(forms.Form):
#    products_choices = []
#    products = Product.objects.all()
#    for product in products:
#        products_choices.append((product.pk,product.name))
#    
#    products = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices = products_choices)

#class VendorDealForm(forms):
#class VendorDealForm(forms):


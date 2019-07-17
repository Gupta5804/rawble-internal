from django.contrib import admin
from .models import ContactBuyer,ContactVendor
# Register your models here.
 

class ContactBuyerAdmin(admin.ModelAdmin):
    list_display = ('contact_name','first_name','last_name','status','email','mobile','payment_terms','outstanding_receivable','outstanding_payable','relationship_manager')
class ContactVendorAdmin(admin.ModelAdmin):
    list_display = ('contact_name','first_name','last_name','status','email','mobile','payment_terms','outstanding_receivable','outstanding_payable','relationship_manager')


admin.site.register(ContactBuyer,ContactBuyerAdmin)
admin.site.register(ContactVendor,ContactVendorAdmin)
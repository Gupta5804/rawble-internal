from django.contrib import admin
from reports.models import Invoice,Bill

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_id','date','product','customer_name','quantity','price']
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_id','date','product','vendor_name','quantity','price']
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Bill,BillAdmin)
# Register your models here.

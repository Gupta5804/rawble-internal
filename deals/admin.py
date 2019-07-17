from django.contrib import admin
from .models import DealVendorProduct,DealVendor,VendorProduct,VendorProductVariation,ZohoEstimate,EstimateProduct,ZohoSalesOrder,SalesOrderProduct,ZohoPurchaseOrder,PurchaseOrderProduct
# Register your models here.


class ZohoSalesOrderAdmin(admin.ModelAdmin):
    list_display=('salesorder_number','status')    

admin.site.register(DealVendor)
admin.site.register(DealVendorProduct)
admin.site.register(VendorProduct)
admin.site.register(VendorProductVariation)
admin.site.register(ZohoEstimate)
admin.site.register(EstimateProduct)
admin.site.register(ZohoSalesOrder,ZohoSalesOrderAdmin)
admin.site.register(SalesOrderProduct)
admin.site.register(ZohoPurchaseOrder)
admin.site.register(PurchaseOrderProduct)


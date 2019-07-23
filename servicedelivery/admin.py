from django.contrib import admin
from servicedelivery.models import Transporter,SalesOrderProductPlan,PurchaseOrderProductPlan
admin.site.register(Transporter)
admin.site.register(SalesOrderProductPlan)
admin.site.register(PurchaseOrderProductPlan)
# Register your models here.

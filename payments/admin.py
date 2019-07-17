from django.contrib import admin
from .models import Payment
from ordered_model.admin import OrderedModelAdmin
# Register your models here.
class PaymentAdmin(OrderedModelAdmin):
    list_display = ['vendor','amount','move_up_down_links']
admin.site.register(Payment,PaymentAdmin)

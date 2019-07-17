from django.contrib import admin 
from .models import Product,ProductGroup,Make,Unit,CoaFile

class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','hsn_or_sac','status','stock_on_hand')


admin.site.register(CoaFile)
admin.site.register(Make)
admin.site.register(Unit)
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductGroup,ProductGroupAdmin)




# Register your models here.

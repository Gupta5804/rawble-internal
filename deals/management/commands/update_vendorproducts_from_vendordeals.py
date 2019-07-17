from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import DealVendor,DealVendorProduct,VendorProduct,VendorProductVariation


class Command(BaseCommand):
    help = 'Updates Vendor Products from Vendor Deals'
    def handle(self,*args,**kwargs):
        dealproducts = DealVendorProduct.objects.all().order_by('id')
        for vendorproduct in VendorProduct.objects.all():
            if(vendorproduct.vendorproductvariation_set.all()):
                pass
            else:
                vendorproduct.delete()
        for dealproduct in dealproducts:
            try:
                vendorproduct = VendorProduct.objects.get(vendor = dealproduct.deal.vendor , product = dealproduct.product )
                try:
                    vendorproductvariation = VendorProductVariation.objects.get(vendorproduct = vendorproduct , dealvendorproduct__specs = dealproduct.specs , dealvendorproduct__quantity = dealproduct.quantity)
                    vendorproductvariation.dealvendorproduct = dealproduct 
                    vendorproductvariation.save()
                except:
                    vendorproductvariation = VendorProductVariation(vendorproduct = vendorproduct , dealvendorproduct = dealproduct)
                    vendorproductvariation.save()
            except:
                vendorproduct = VendorProduct(vendor = dealproduct.deal.vendor , product = dealproduct.product)
                vendorproduct.save()
                vendorproductvariation = VendorProductVariation(vendorproduct = vendorproduct , dealvendorproduct = dealproduct)
                vendorproductvariation.save()

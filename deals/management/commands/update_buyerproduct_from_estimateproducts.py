from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import DealVendor,DealVendorProduct,VendorProduct,VendorProductVariation,EstimateProduct,BuyerProduct


class Command(BaseCommand):
    help = 'Updates Buyer Products from Estimate Products'
    def handle(self,*args,**kwargs):
        estimateproducts = EstimateProduct.objects.all()
        for estimateproduct in estimateproducts :
            buyer = estimateproduct.estimate.buyer
            product = estimateproduct.product

            try:
                buyerproduct = BuyerProduct.objects.get(buyer = buyer , product = product)

            except:
                buyerproduct = BuyerProduct(buyer = buyer , product= product)

                buyerproduct.save()

from django.core.management.base import BaseCommand
from deals.models import ZohoEstimate,ZohoSalesOrder,SalesOrderProduct
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage,EmailMultiAlternatives
import requests
from products.models import Product
class Command(BaseCommand):
    help = 'Updates Buyer Products And Buyer Product Month Sales'
    def handle(self,*args,**kwargs):
        so_number = "SO-001406"
        zoho_location = "okhla"
        so = ZohoSalesOrder.objects.get(salesorder_number=so_number , zoho_location=zoho_location)
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        parameters={'authtoken':auth_token}
        organization_ids = {'okhla':'667580392','baddi':'665963577'}
        parameters['organization_id'] = organization_ids[so.zoho_location]
        response=requests.get("https://books.zoho.com/api/v3/salesorders/"+str(so.salesorder_id),params = parameters)
        print(response.text)
        salesorder_api = response.json()['salesorder']

        for item in salesorder_api['line_items']:
            sop_qs = SalesOrderProduct.objects.filter(salesorder=so,product = Product.objects.get(pk=item['item_id']))
            if(sop_qs):
                if(len(sop_qs) > 1):
                    sop_to_delete = sop_qs[1:]
                    sop_to_delete.delete()
                sop = sop_qs[0]
                sop.so_selling_price = item['rate']
                sop.quantity = item['quantity']
                sop.save()
            else:
                sop = SalesOrderProduct(
                    salesorder = so,
                    product = Product.objects.get(pk=item['item_id']),
                    quantity = item['quantity'],
                    so_selling_price = item['rate'],
                    )
                sop.save()
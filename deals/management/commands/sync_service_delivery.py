from django.core.management.base import BaseCommand
from django.core.management import call_command
import requests
import json
import itertools
from deals.models import ZohoSalesOrder,ZohoEstimate,SalesOrderProduct
from servicedelivery.models import SalesOrderProductPlan
from products.models import Product
from contacts.models import ContactBuyer
from django.contrib.auth.models import User
import pandas as pd
import datetime

class Command(BaseCommand):
    help = 'Updates salesorders from Zoho Books'
    def handle(self,*args,**kwargs):
        sopps = SalesOrderProductPlan.objects.all()
        for sopp in sopps:
            
            if(sopp.plan_status == "planned" and sopp.transporter == None):
                print("2->",sopp.transporter)
                sopp.shipped_date_time = sopp.planned_date_time
                sopp.delivered_date_time = sopp.planned_date_time
                sopp.save()
        #base_url = "https://books.zoho.com/api/v3"
        #end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills',#'items':'/items','estimates':'/estimates','salesorders':'/salesorders'}
        #auth_token = 'd56b2f2501f266739e12b86b706d0078'
        #organization_id = '667580392'
        #parameters={'authtoken':auth_token,'organization_id':organization_id}
        #
        #df_invoice = pd.read_excel("Invoice.xls",sheet_name="Invoice")
        ##print(df_invoice.columns)
        #salesorders= ZohoSalesOrder.objects.all()
        #for salesorder in salesorders:
        #    if(salesorder.planned_status == False):
        #        if(salesorder.salesorderproduct_set.count() == 0):
#
        #            response = requests.get(base_url + end_points['salesorders'] + "/"+str(salesorder.salesorder_id),#params = parameters)
        #            salesorder_api = response.json()['salesorder']
        #            for item in salesorder_api['line_items']:
        #                item['pack_size'] = 0
        #                for item_custom_field in item['item_custom_fields']:
        #                    if item_custom_field['label'] == 'Pack Size':
        #                        item['pack_size'] = item_custom_field['value']
        #                try:
        #                    sop = salesorder.salesorderproduct_set.get(product__item_id = item['item_id'])
        #                except:
#
        #                    sop = SalesOrderProduct(
        #                        salesorder = salesorder,
        #                        product = Product.objects.get(item_id = item['item_id']), #check
        #                        vendorproductvariation = None,
        #                        quantity = item['quantity'],
        #                        pack_size = item['pack_size'],
        #                        so_selling_price = item['rate']
        #                    )
        #                    sop.save()
        #        for index,rows in df_invoice.iterrows():
        #            if(str(salesorder.salesorder_number) in str(rows['PurchaseOrder'])):
        #                print("excel product-->" , rows['Item Name'])
        #                print("salesorder products")
        #                for sop in salesorder.salesorderproduct_set.all():
        #                    print(sop.product.name)
        #                try:
        #                    sopp = SalesOrderProductPlan(
        #                        salesorderproduct = salesorder.salesorderproduct_set.get(product__item_id = rows['Product #ID']),
        #                        planned_date_time =datetime.datetime.strptime(rows["Invoice Date"],"%Y-%m-%d"),
        #                        planned_quantity = rows['Quantity'],
        #                        freight = 0,
        #                    )
        #                    sopp.save()
        #                except:
        #                    pass

                    


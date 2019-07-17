from django.core.management.base import BaseCommand
from django.core.management import call_command
import requests
import json
import itertools
from deals.models import ZohoSalesOrder,ZohoPurchaseOrder
from contacts.models import ContactVendor
from django.contrib.auth.models import User
class Command(BaseCommand):
    help = 'Updates Purchase Orders from Zoho Books'
    def handle(self,*args,**kwargs):
        base_url = "https://books.zoho.com/api/v3"
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items','estimates':'/estimates','salesorders':'/salesorders','purchaseorders':'/purchaseorders'}
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_id = '667580392'
        page_number = 1
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        parameters['page'] = page_number

        list_purchaseorders = []
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['purchaseorders'],params = parameters)
            purchaseorders = response.json()['purchaseorders']
            list_purchaseorders.append(purchaseorders)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
        print(len(list_purchaseorders))
        list_purchaseorder_ids = []
        for page in list_purchaseorders:
            for purchaseorder in page:
                try:
                    vendor = ContactVendor.objects.get(pk = purchaseorder['vendor_id'])
                except:
                    call_command('contacts_update_from_zoho')
                    vendor = ContactVendor.objects.get(pk = purchaseorder['vendor_id'])
                purchaseorder_id = purchaseorder['purchaseorder_id']
                status = purchaseorder['status']
                status = purchaseorder['status']
                
                billed_status = purchaseorder['billed_status']
                purchaseorder_number = purchaseorder['purchaseorder_number']
                reference_number = purchaseorder['reference_number']
                date = purchaseorder['date']
                delivery_date = purchaseorder['delivery_date']
                
                
                list_purchaseorder_ids.append(purchaseorder_id)
                total = purchaseorder['total']
                purchaseorder_url = "https://books.zoho.com/app#/purchaseorders/" + purchaseorder_id
                if(date == ""):
                    date = None
                if(delivery_date == ""):
                    delivery_date = None
                try:
                    #estimate_number = salesorder['reference_number'].split("/")[0].strip()
                    salesorder = ZohoSalesOrder.objects.get(salesorder_number = reference_number)
                except:
                    salesorder = None
                try:
                    z1 = ZohoPurchaseOrder.objects.get(purchaseorder_id = purchaseorder_id)
                    print('PO Exists !, Updating fields')
                    
                    z1.status = status
                    
                    
                    z1.billed_status = billed_status
                    z1.status = status
                    z1.salesorder = salesorder
                    z1.total = total
                    z1.save()
                except:
                    print('PO doesnt exist ! Adding to DB')
                    z1 = ZohoPurchaseOrder(
                        vendor = vendor,
                        purchaseorder_id = purchaseorder_id,
                        billed_status = billed_status,
                        
                        status = status,
                        purchaseorder_number = str(purchaseorder_number),
                        date = date,
                        
                        total = total,
                        purchaseorder_url = purchaseorder_url,
                        salesorder = salesorder
                        )
                    z1.save()
        
from django.core.management.base import BaseCommand
from django.core.management import call_command
import requests
import json
import itertools
from deals.models import ZohoSalesOrder,ZohoEstimate,SalesOrderProduct
from products.models import Product
from contacts.models import ContactBuyer
from django.contrib.auth.models import User
class Command(BaseCommand):
    help = 'Updates salesorders from Zoho Books'
    def handle(self,*args,**kwargs):
        base_url = "https://books.zoho.com/api/v3"
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items','estimates':'/estimates','salesorders':'/salesorders'}
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_ids = {'okhla':'667580392','baddi':'665963577'}
        organization_id = organization_ids['okhla']
        page_number = 1
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        parameters['page'] = page_number

        list_salesorders = []
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['salesorders'],params = parameters)
            salesorders = response.json()['salesorders']
            list_salesorders.append(salesorders)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
        print(len(list_salesorders))
        list_salesorder_ids = []
        for page in list_salesorders:
            for salesorder in page:
                try:
                    buyer = ContactBuyer.objects.get(pk = salesorder['customer_id'])
                except:
                    call_command('contacts_update_from_zoho')
                    buyer = ContactBuyer.objects.get(pk = salesorder['customer_id'])
                salesorder_id = salesorder['salesorder_id']
                status = salesorder['current_sub_status']
                salesorder_number = salesorder['salesorder_number']
                reference_number = salesorder['reference_number']
                date = salesorder['date']
                
                salesperson = salesorder['salesperson_name']
                list_salesorder_ids.append(salesorder_id)
                total = salesorder['total']
                salesorder_url = "https://books.zoho.com/app#/salesorders/" + salesorder_id
                try:
                    estimate_number = salesorder['reference_number'].split("/")[0].strip()
                    estimate = ZohoEstimate.objects.get(estimate_number = estimate_number,zoho_location = "okhla")
                except:
                    estimate = None
                z1=ZohoSalesOrder.objects.filter(salesorder_id = salesorder_id)
                parameters={'authtoken':auth_token,'organization_id':organization_id}
                if(z1):
                    
                    print('SO Exists !, Updating fields')
                    z1.update(salesperson = salesperson)
                    #z1.update(status = status)
                    z1.update(estimate = estimate)
                    z1.update(total = total)
                    so = z1[0]
                    #if(so.salesorderproduct_set.count() == 0):
                    #    
                    #    print("saving SO items to DB SO#:",so.salesorder_number)
                    #    response = requests.get(base_url + end_points['salesorders']+"/"+str(salesorder_id),params = #parameters)
                    #    salesorder_api = response.json()['salesorder']
                    #    for item in salesorder_api['line_items']:
                    #        pack_size = 0
                    #        for custom_field in item['item_custom_fields']:
                    #            if(custom_field["placeholder"] == "cf_pack_size"):
                    #                pack_size = custom_field["value"]
                    #    try:
                    #        sop = SalesOrderProduct(
                    #            salesorder = so,
                    #            product = Product.objects.get(item_id = item['item_id']),
                    #            quantity = item['quantity'],
                    #            pack_size = pack_size,
                    #            so_selling_price = item['rate'])
                    #        sop.save()
                    #    except:
                    #        pass

                else:
                    print('SO doesnt exist ! Adding to DB')
                    zso = ZohoSalesOrder(
                        buyer = buyer,
                        salesorder_id = salesorder_id,
                        status = status,
                        salesorder_number = salesorder_number,
                        date = date,
                        total = total,
                        salesorder_url = salesorder_url,
                        tool_status = '',
                        salesperson = salesperson,
                        estimate = estimate

                    )
                    zso.save()
                    #if(zso.salesorderproduct_set.count() == 0):
                    #    print("saving SO items to DB SO#:",zso.salesorder_number)
                    #    response = requests.get(base_url + end_points['salesorder']+"/"+str(salesorder_id),params = #parameters)
                    #    salesorder_api = response.json()['salesorders']
                    #    for item in salesorder_api['line_items']:
                    #        pack_size = 0
                    #        for custom_field in item['item_custom_fields']:
                    #            if(custom_field["placeholder"] == "cf_pack_size"):
                    #                pack_size = custom_field["value"]
                    #        sop = SalesOrderProduct(
                    #            salesorder = zso,
                    #            product = Product.objects.get(item_id = item['item_id']),
                    #            quantity = item['quantity'],
                    #            pack_size = pack_size,
                    #            so_selling_price = item['rate'])
                    #        sop.save()
        
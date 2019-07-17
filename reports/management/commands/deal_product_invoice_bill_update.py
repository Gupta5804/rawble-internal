from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import DealBuyer
from reports.models import Invoice,Bill
class Command(BaseCommand):
    help = 'Updates invoices and bills'
    def add_arguments(self,parser):

        parser.add_argument('deal_id', type=int, help='Indicates the Deal id')


    def handle(self,*args,**kwargs):
        deal_id = kwargs['deal_id']
        base_url = "https://books.zoho.com/api/v3"
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_id = '667580392'

        parameters={'authtoken':auth_token,'organization_id':organization_id}


        buyerdeal_set = DealBuyer.objects.get(id=deal_id)

        #for deal in buyerdeals_set:
        for dealproduct in buyerdeal_set.dealbuyerproduct_set.all():
            print(dealproduct.product_group,"-->")
            for product in dealproduct.product_group.product_set.all():
                page_number = 1
                parameters['page'] = page_number
                parameters['item_id'] = product.pk

                list_invoices = []
                list_bills = []
                for i in itertools.count():
                    parameters['page'] = page_number + i
                    response = requests.get(base_url + end_points['invoices'],params = parameters)
                    invoices = response.json()['invoices']
                    list_invoices.append(invoices)
                    print(parameters)
                    if(response.json()['page_context']['has_more_page'] != True):
                        break
                page_number = 1
                for i in itertools.count():
                    parameters['page'] = page_number + i
                    response = requests.get(base_url + end_points['bills'],params = parameters)
                    bills = response.json()['bills']
                    list_bills.append(bills)
                    print(parameters)
                    if(response.json()['page_context']['has_more_page'] != True):
                        break
                for page in list_invoices:
                    for invoice in page:
                        invoice_id = invoice['invoice_id']
                        customer_name = invoice['customer_name']
                        date = invoice['date']
                        quantity = invoice['item_quantity']
                        price = invoice['item_price']
                        url = invoice['invoice_url']

                        #print(invoice_id,customer_name,date,quantity,date,price,url)

                        I1 = Invoice.objects.filter(invoice_id=invoice_id,product = product)
                        if(I1):
                            print("Invoice Already Exists")

                        else:
                            print("Invoice Does Not Exist")
                            I = Invoice(
                                    invoice_id = invoice_id,
                                    customer_name = customer_name,
                                    date= date,
                                    quantity = quantity,
                                    price = price,
                                    url = url,
                                    product = product
                                    )
                            I.save()
                            print("Invoice Added")
                for page in list_bills:
                    for bill in page:
                        bill_id = bill['bill_id']
                        vendor_name = bill['vendor_name']
                        date = bill['date']
                        quantity = bill['item_quantity']
                        price = bill['item_price']


                        #print(invoice_id,customer_name,date,quantity,date,price,url)

                        B1 = Bill.objects.filter(bill_id=bill_id,product=product)
                        if(B1):
                            print("Bill Already Exists")

                        else:
                            print("Bill Does Not Exist")
                            B = Bill(
                                bill_id = bill_id,
                                vendor_name = vendor_name,
                                date= date,
                                quantity = quantity,
                                price = price,

                                product = product
                            )
                            B.save()
                            print("Bill Added")

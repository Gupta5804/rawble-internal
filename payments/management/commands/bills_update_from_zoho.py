from django.core.management.base import BaseCommand
import requests
import json
import itertools
from payments.models import Payment
from contacts.models import ContactVendor

class Command(BaseCommand):
    help = 'Updates products from Zoho Books'
    def handle(self,*args,**kwargs):
        base_url = "https://books.zoho.com/api/v3"
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_id = '667580392'
        page_number = 1
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        parameters['page'] = page_number
        parameters['status'] = 'overdue'
        list_bills = []
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['bills'],params = parameters)
            bills = response.json()['bills']
            list_bills.append(bills)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
        print(len(list_bills))
        for page in list_bills:
            for bill in page:
                vendor = ContactVendor.objects.get(pk = bill['vendor_id'])
                amount = bill['balance']
                date = bill['date']
                try:
                    delivery_terms = bill['cf_delivery_terms']
                except:
                    delivery_terms = ''
                bill_url = "https://books.zoho.com/app#/bills/" + bill['bill_id']
                due_date = bill['due_date']
                bill_number= bill['bill_number']
                bill_id= bill['bill_id']
                bill_status = bill['status']
                due_days = bill['due_days']
                bill_total = bill['total']
                bill_time_created = bill['created_time']

                try:
                    p1 = Payment.objects.get(payment_type = 'unpaid_bill',bill_id = bill_id)
                    print('Bill Exists !, Updating fields')

                    p1.amount = amount
                    p1.due_days = due_days
                    p1.date = date
                    p1.save()
                except:
                    print('bill doesnt exist ! Adding to DB')
                    p1 = Payment(
                        payment_type = 'unpaid_bill',
                        vendor = vendor,
                        amount = amount,
                        date = date,
                        delivery_terms=delivery_terms,
                        bill_url = bill_url,
                        due_date = due_date,
                        bill_number = bill_number,
                        bill_id = bill_id,
                        bill_status=bill_status,
                        due_days=due_days,
                        bill_total=bill_total,
                        bill_time_created = bill_time_created

                    )
                    p1.save()

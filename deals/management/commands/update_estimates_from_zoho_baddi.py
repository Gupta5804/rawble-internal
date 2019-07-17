from django.core.management.base import BaseCommand
from django.core.management import call_command
import requests
import json
import itertools
from deals.models import ZohoEstimate
from contacts.models import ContactBuyer
from django.contrib.auth.models import User
class Command(BaseCommand):
    help = 'Updates estimates from Zoho Books'
    def handle(self,*args,**kwargs):
        base_url = "https://books.zoho.com/api/v3"
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items','estimates':'/estimates'}
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_ids = {'okhla':'667580392','baddi':'665963577'}
        organization_id = organization_ids['baddi']
        page_number = 1
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        parameters['page'] = page_number

        list_estimates = []
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['estimates'],params = parameters)
            estimates = response.json()['estimates']
            list_estimates.append(estimates)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
        print(len(list_estimates))
        list_estimate_ids = []
        for page in list_estimates:
            for estimate in page:
                try:
                    buyer = ContactBuyer.objects.get(pk = estimate['customer_id'])
                except:
                    call_command('contacts_update_from_zoho')
                    buyer = ContactBuyer.objects.get(pk = estimate['customer_id'])
                estimate_id = estimate['estimate_id']
                status = estimate['status']
                estimate_number = estimate['estimate_number']
                date = estimate['date']
                expiry_date = estimate['expiry_date']
                salesperson = estimate['salesperson_name']
                list_estimate_ids.append(estimate_id)
                try:
                    delivery_terms = estimate['cf_delivery_terms']
                except:
                    delivery_terms = ''
                total = estimate['total']
                estimate_url = "https://books.zoho.com/app#/quotes/" + estimate_id
                if(expiry_date==''):
                    expiry_date = '1111-11-11'
                z1 = ZohoEstimate.objects.filter(estimate_id = estimate_id)
                if(z1):
                    print('estimate Exists !, Updating fields')
                    z1.update(salesperson = salesperson)
                    z1.update(status = status)
                    z1.update(expiry_date = expiry_date)
                    z1.update(total = total)
                    
                else:
                    print('estimate doesnt exist ! Adding to DB')
                    z = ZohoEstimate(
                        buyer = buyer,
                        estimate_id = estimate_id,
                        status = status,
                        estimate_number = estimate_number,
                        date = date,
                        expiry_date = expiry_date,
                        delivery_terms = delivery_terms,
                        total = total,
                        estimate_url = estimate_url,
                        tool_status = '',
                        salesperson = salesperson,
                        zoho_location = "baddi"
                    )
                    z.save()
        

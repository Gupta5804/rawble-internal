#auth_token = d56b2f2501f266739e12b86b706d0078

from django.core.management.base import BaseCommand
import requests
import json
import itertools
from products.models import Product,Make,Unit

class Command(BaseCommand):
    help = 'Updates products from Zoho Books'

    def handle(self,*args,**kwargs):
        base_url = "https://books.zoho.com/api/v3"
        end_points = {'invoices':'/invoices','crm':'/crm','contacts':'/contacts','account':'/account','bills':'/bills','items':'/items'}
        auth_token = 'd56b2f2501f266739e12b86b706d0078'
        organization_ids = {'okhla':'667580392','baddi':'665963577'}
        organization_id = organization_ids['baddi']
        page_number = 1
        parameters={'authtoken':auth_token,'organization_id':organization_id}
        parameters['page'] = page_number
        list_products = []
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['items'],params = parameters)
            items = response.json()['items']
            list_products.append(items)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
        print(len(list_products))
        for page in list_products:
            for item in page:
                #print(item)
                item_id = int(item['item_id'])
                hsn_or_sac = item['hsn_or_sac']
                name = item['name']
                description = item['description']
                unit = item['unit']
                if(item['status'] == 'active'):
                    status = 'Ac'
                else:
                    status ='In'
                product_type = item['product_type']
                sku = item['sku']
                try:
                    make = item['cf_make']
                except:
                    make = ""
                try:
                    stock_on_hand = item['stock_on_hand']
                except:
                    stock_on_hand = 0

                if(make == ""):
                    pass
                else:
                    m1 = Make.objects.filter(name=make)
                    if(m1):
                        print(make,' Already Exists !','Skipping')
                    else:
                        print(make,'Doesnt Exist !','Adding to Database')
                        m = Make(name=make)
                        m.save()
                        print(make,'Added to Database')
                try:
                    u1 = Unit.objects.filter(name=unit)
                    print(unit,'Already Exists !')
                except:
                    print(unit,'Doesnt Exist !','Adding to Database')
                    u1 = Unit(name=unit)
                    u1.save()
                    print(unit,'Added to Database')
                
                try:
                    p1 = Product.objects.get(pk = item_id)
                    print(name,' Already Exists !',' updating field values !')

                    p1.hsn_or_sac = hsn_or_sac
                    p1.name = (name)
                    p1.description = description
                    p1.unit = unit
                    p1.status = status
                    p1.product_type = product_type
                    p1.sku = sku
                    p1.make = make
                    p1.stock_on_hand = stock_on_hand

                    p1.save()
                except:
                    print(name,' Does Not exist , Adding now')
                    p1 = Product(
                        item_id = item_id,
                        hsn_or_sac = hsn_or_sac,
                        name =(name),
                        description=description,
                        unit = unit,
                        status =status,
                        product_type =product_type,
                        sku = sku,
                        stock_on_hand = stock_on_hand,
                        make=make,
                        zoho_location="baddi"
                        )
                    p1.save()
                    print(name, ' Added to Database')

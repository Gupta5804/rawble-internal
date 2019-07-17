#auth_token = d56b2f2501f266739e12b86b706d0078

from django.core.management.base import BaseCommand
import requests
import json
import itertools
from contacts.models import ContactBuyer , ContactVendor

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
        list_contacts = []
        for i in itertools.count():
            parameters['page'] = page_number + i
            response = requests.get(base_url + end_points['contacts'],params = parameters)
            contacts = response.json()['contacts']
            list_contacts.append(contacts)
            print(parameters)
            if(response.json()['page_context']['has_more_page'] != True):
                break
        print(len(list_contacts))
        for page in list_contacts:
            for contact in page:
                #print(item)
                contact_id = int(contact['contact_id'])
                contact_name = contact['contact_name']
                website = contact['website']
                first_name = contact['first_name']
                last_name = contact['last_name']

                if(contact['status'] == 'active'):
                    status = 'Ac'
                else:
                    status ='In'
                
                if(contact['contact_type'] == 'customer'):
                    contact_type = 'C'
                else:
                    contact_type ='V'
                
                email = contact['email']
                phone = contact['phone']
                mobile = contact['mobile']
                payment_terms = contact['payment_terms_label']
                outstanding_receivable = contact['outstanding_receivable_amount']
                outstanding_payable = contact['outstanding_payable_amount']
                place_of_contact = contact['place_of_contact_formatted']
                currency_code = contact['currency_code']
                gst_no = contact['gst_no']
                try:
                    place_of_contact = contact['place_of_contact_formatted']
                except:
                    place_of_contact = ""
                try:
                    relationship_manager = contact['cf_relationship_manager']
                except:
                    relationship_manager = " "
                
                
                try:
                    if (contact_type == 'C'):
                        c1 = ContactBuyer.objects.get(pk = contact_id)
                    else:
                        c1 = ContactVendor.objects.get(pk = contact_id)

                    print(contact_name,' Already Exists !', ' updating now...!')
                    c1.contact_name = contact_name
                    c1.website = website
                    c1.first_name = first_name
                    c1.last_name = last_name
                    c1.status = status
                    c1.contact_type = contact_type
                    c1.email = email
                    c1.phone = phone
                    c1.mobile = mobile
                    c1.payment_terms = payment_terms
                    c1.outstanding_receivable = outstanding_receivable
                    c1.outstanding_payable = outstanding_payable
                    c1.place_of_contact = place_of_contact
                    c1.currency_code = currency_code
                    c1.gst_no = gst_no
                    c1.relationship_manager = relationship_manager
                    c1.place_of_contact = place_of_contact
                    c1.save()
                except:
                    print(contact_name,' Does Not exist , Adding now') 
                    if(contact_type == 'C'):
                        c1 = ContactBuyer(
                            contact_id=contact_id, 
                            contact_name=contact_name, 
                            website=website, 
                            #contact_type=contact_type, 
                            first_name=first_name, 
                            last_name=last_name, 
                            status=status, 
                            email=email, 
                            phone=phone, 
                            mobile=mobile, 
                            payment_terms=payment_terms, 
                            outstanding_receivable=outstanding_receivable, 
                            outstanding_payable=outstanding_payable, 
                            place_of_contact=place_of_contact, 
                            currency_code=currency_code, 
                            relationship_manager=relationship_manager,
                            gst_no=gst_no,
                            zoho_location="baddi" )
                    else:
                        c1 = ContactVendor(
                            contact_id=contact_id, 
                            contact_name=contact_name, 
                            website=website, 
                            #contact_type=contact_type, 
                            first_name=first_name, 
                            last_name=last_name, 
                            status=status, 
                            email=email, 
                            phone=phone, 
                            mobile=mobile, 
                            payment_terms=payment_terms, 
                            outstanding_receivable=outstanding_receivable, 
                            outstanding_payable=outstanding_payable, 
                            place_of_contact=place_of_contact, 
                            currency_code=currency_code, 
                            relationship_manager=relationship_manager,
                            gst_no=gst_no,
                            zoho_location="baddi" )
                    
                    c1.save()
                    print(contact_name, ' Added to Database')

        
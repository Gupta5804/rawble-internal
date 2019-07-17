from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import SalesOrderProduct
from datetime import datetime
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags
from datetime import datetime,timedelta
class Command(BaseCommand):
    help = 'Updates products from Zoho Books'

    def handle(self,*args,**kwargs):
        outward_sop= SalesOrderProduct.objects.filter(outward_date_time__date=(datetime.today() - timedelta(days=1)))
        print(outward_sop)
        sop_email=[]
        for sop in outward_sop :
            print(sop.salesorder.salesorder_number)
        
            sop.quantity_dispatched = sop.quantity_dispatched + sop.quantity_to_dispatch
                
                
            sop.save()
                
            sop_email.append(sop)
        if( sop_email ):
            subject = "Items Dispatched YesterDay (Reminder)"
            to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
            from_email = 'admin@rawble.com'
            users = User.objects.all()
            users_sales = User.objects.filter(groups__name="Sales Team")
            total_quantity = 0
            total_amount = 0
            for sop in sop_email:
                total_quantity = total_quantity + sop.quantity_to_dispatch
                total_amount = total_amount + ( sop.quantity_to_dispatch * sop.so_selling_price )
            ctx = {
                "sop_email":sop_email,
                "users_sales":users_sales,
                "total_quantity":total_quantity,
                "total_amount":total_amount

                }
            for user in users:
                to.append(str(user.email))


            message = render_to_string('emails/outward_dispatched.html', ctx)
            text_content = strip_tags(message)
            #EmailMessage(subject, message, to=to, from_email=from_email).send()
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(message, "text/html")
            msg.send()
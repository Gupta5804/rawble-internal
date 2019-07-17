from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import SalesOrderProduct
from servicedelivery.models import SalesOrderProductPlan
from datetime import datetime
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = 'Updates products from Zoho Books'

    def handle(self,*args,**kwargs):

        
        todays_outward_sopp = SalesOrderProductPlan.objects.filter(planned_date_time__date=datetime.today()).order_by("salesorderproduct__salesorder__salesorder_number")
        total_quantity = 0
        total_amount = 0
        for sopp in todays_outward_sopp:
            total_quantity = total_quantity + sopp.planned_quantity
            total_amount = total_amount + ( sopp.planned_quantity * sopp.salesorderproduct.so_selling_price )
        subject = "Today's Outward Plan|| Date:"+str(datetime.today())
        to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
        from_email = 'admin@rawble.com'
        users = User.objects.all()
        users_sales = User.objects.filter(groups__name="Sales Team")
        ctx = {
            "todays_outward_sopp":todays_outward_sopp,
            "users_sales":users_sales,
            "total_amount":total_amount,
            "total_quantity":total_quantity,


        }
        for user in users:
            to.append(str(user.email))
        

        message = render_to_string('emails/todays_outward.html', ctx)
        text_content = strip_tags(message)
        #EmailMessage(subject, message, to=to, from_email=from_email).send()
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        
        msg.attach_alternative(message, "text/html")
        msg.send()
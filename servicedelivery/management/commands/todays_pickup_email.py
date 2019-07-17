from django.core.management.base import BaseCommand
import requests
import json
import itertools
from deals.models import PurchaseOrderProduct
from datetime import datetime
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMessage,EmailMultiAlternatives
from django.utils.html import strip_tags
class Command(BaseCommand):
    help = 'Updates products from Zoho Books'

    def handle(self,*args,**kwargs):

        
        todays_pickup_pop= PurchaseOrderProduct.objects.filter(pickup_date_time__date=datetime.today())
        print(todays_pickup_pop)
        subject = "Today's Pickup (Reminder)"
        to = ['gupta.rishabh.abcd@gmail.com','rishabh.gupta@rawble.com']
        from_email = 'admin@rawble.com'
        users = User.objects.all()
        users_sales = User.objects.filter(groups__name="Sales Team")
        ctx = {
            "todays_pickup_pop":todays_pickup_pop,
            "users_sales":users_sales,

        }
        for user in users:
            to.append(str(user.email))
        

        message = render_to_string('emails/todays_pickup.html', ctx)
        text_content = strip_tags(message)
        #EmailMessage(subject, message, to=to, from_email=from_email).send()
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(message, "text/html")
        msg.send()
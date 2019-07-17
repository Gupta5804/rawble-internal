from django.core.management.base import BaseCommand
from deals.models import ZohoEstimate
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage,EmailMultiAlternatives

class Command(BaseCommand):
    help = 'Updates Buyer Products And Buyer Product Month Sales'
    def handle(self,*args,**kwargs):
        zoho_estimate = ZohoEstimate.objects.filter(tool_status='',status='draft').order_by("-estimate_number")
        users = User.objects.filter(groups__name="Purchase Team")
        to=[]
        for user in users:
            to.append(str(user.email))
        ctx = {'estimates': zoho_estimate, }
        from_email = 'admin@rawble.com'
        subject = 'Estimates Pending for quotation'
        message = render_to_string('emails/unquoted_estimates.html', ctx)
        # ===========================email====================================
        text_content = strip_tags(message)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(message, "text/html")
        msg.send()

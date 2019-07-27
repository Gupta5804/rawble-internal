from django.shortcuts import render,redirect

from django.views.generic import DeleteView,CreateView
from django.urls import reverse_lazy
from django.core.management import call_command
from servicedelivery.model import PurchaseOrderProductPlan
# Create your views here.
def payments_payable_nextpayment(request):
    return render(request,'payments/payable_nextpayment.html')
def payments_payable_chequeapproval(request):
    return render(request,'payments/payable_chequeapproval.html')
def payments_payable_pending(request):

    return render(request,'payments/payable_pending.html')


#def advancepayment_reorder(request):
#    payments = Payment.objects.all()
#    return render(request,'payments/advance_payment_reorder.html',{'payments':payments})
#
#def payment_reorder_moveup(request,pk):
#    payment = Payment.objects.get(id=pk)
#    payment.up()
#    return redirect('advance_payment_reorder')
#def payment_reorder_movedown(request,pk):
#    payment = Payment.objects.get(id=pk)
#    payment.down()
#    return redirect('advance_payment_reorder')

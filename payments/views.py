from django.shortcuts import render,redirect
from payments.models import Payment
from django.views.generic import DeleteView,CreateView
from django.urls import reverse_lazy
from django.core.management import call_command
# Create your views here.
def payments_payable_nextpayment(request):
    return render(request,'payments/receivable_nextpayment.html')
def payments_payable_chequeapproval(request):
    return render(request,'payments/receivable_chequeapproval.html')
def payments_payable_pending(request):
    return render(request,'payments/receivable_pending.html')

def payment(request):
    payments = Payment.objects.all()
    return render(request,'payments/payment.html',{'payments':payments})
#def advancepayment(request):
#    payments = Payment.objects.all()
#    return render(request,'payments/advance_payment.html',{'payments':payments})
#
class PaymentDelete(DeleteView):
    model = Payment
    success_url = reverse_lazy('payment')
class PaymentCreate(CreateView):
    model=Payment
    fields = ['date','vendor','amount','reason','comment','delivery_terms']
    success_url = reverse_lazy('payment')
def payment_moveup(request,pk):
    payment = Payment.objects.get(id=pk)
    payment.up()
    return redirect('payment')

def payment_movedown(request,pk):
    payment = Payment.objects.get(id=pk)
    payment.down()
    return redirect('payment')

def payment_movetop(request,pk):
    payment = Payment.objects.get(id=pk)
    payment.top()
    return redirect('payment')

def payment_movebottom(request,pk):
    payment = Payment.objects.get(id=pk)
    payment.bottom()
    return redirect('payment')
def refresh_unpaid_bills(request):
    call_command('bills_update_from_zoho')
    return redirect('payment')

def toggle_check_sent_status(request,pk):
    payment = Payment.objects.get(id=pk)
    if(payment.check_sent_status == True):
        payment.check_sent_status =False
    else:
        payment.check_sent_status = True
    payment.save()
    return redirect('payment')
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

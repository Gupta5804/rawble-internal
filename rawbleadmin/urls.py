"""rawbleadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import dashboard,refresh_contacts,refresh_products,SeeAll
from products import views as product_views
from contacts import views as contact_views
from deals import views as deal_views
from payments import views as payment_views
from servicedelivery import views as servicedelivery_views
#from payments.views import advancepayment,AdvancePaymentDelete,AdvancePaymentCreate,advancepayment_reorder,advancepayment_reorder_moveup,advancepayment_reorder_movedown

class DangerousLoginView(LoginView):
    '''A LoginView with no CSRF protection.'''

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_exempt)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    'Redirection loop for authenticated user detected. Check that '
                    'your LOGIN_REDIRECT_URL doesn\'t point to a login page.')
            return HttpResponseRedirect(redirect_to)
        return super(LoginView, self).dispatch(request, *args, **kwargs)








urlpatterns = [
    #path('accounts/login/',DangerousLoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
        #accounts/login/ [name='login']
        #accounts/logout/ [name='logout']
        #accounts/password_change/ [name='password_change']
        #accounts/password_change/done/ [name='password_change_done']
        #accounts/password_reset/ [name='password_reset']
        #accounts/password_reset/done/ [name='password_reset_done']
        #accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
        #accounts/reset/done/ [name='password_reset_complete']
    #path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('',dashboard,name="home"),
    path('seeall',SeeAll,name="seeall"),
    path('refresh/products/',refresh_products,name="refresh_products"),
    path('refresh/contacts/',refresh_contacts,name="refresh_contacts"),
    path('refresh/purchase_orders/',servicedelivery_views.refresh_purchase_orders,name='refresh_purchase_orders'),
    #path('refresh/unpaid_bills/',payment_views.refresh_unpaid_bills,name='refresh_unpaid_bills'),
    path('refresh/sales_orders/',servicedelivery_views.refresh_sales_order,name='refresh_sales_orders'),
    path('products_listing/',product_views.FilteredProductListView.as_view(),name='products_listing'),
    path('products_listing_post/',product_views.products_listing,name='products_listing_post'),
    path('products_listing/filter',product_views.filtering_query,name='export_filtered_query'),
    path('coa_upload/<int:pk>/',product_views.CoaFileUploadView.as_view(),name='coa_upload'),
    path('product_history/sales/<int:pk>/',product_views.product_sales_history,name='product_sales_history'),
    path('product_history/purchase/<int:pk>/',product_views.product_purchase_history,name='product_purchase_history'),
    path('recent_deals/<int:pk>/',product_views.recent_deals,name='recent_deals'),

    path('make/',product_views.MakeListView.as_view(),name='make_list'),
    path('make/create',product_views.MakeCreateView.as_view(),name='make_create'),
    path('make/delete/<int:pk>',product_views.MakeDeleteView.as_view(),name='make_delete'),

    path('product_groups/',product_views.ProductGroupList,name='product_group_list'),
    path('product_groups/create/',product_views.ProductGroupCreate,name='product_group_create'),
    path('product_groups/<int:pk>/',product_views.ProductGroupDetailView.as_view(),name='product_group_detail'),
    path('product_groups/<int:pk1>/product_remove/<int:pk2>/',product_views.product_group_product_remove,name='product_group_product_remove'),
    path('product_groups/add_more_products/<int:pk1>',product_views.product_group_add_products,name='product_group_add_product'),
    path('product_groups/delete/<int:pk>/',product_views.ProductGroupDeleteView.as_view(),name='product_group_delete'),


    path('vendors_listing/',contact_views.vendors_listing,name='vendors_listing'),
    path('vendor_profile/<int:contact_id>/',contact_views.vendor_profile,name='vendor_profile'),
    
    path('buyers_listing/',contact_views.buyers_listing,name='buyers_listing'),
    path('buyer_profile/<int:contact_id>/',contact_views.buyer_profile,name='buyer_profile'),

    path('django_plotly_dash', include('django_plotly_dash.urls')),

    
    path('deals/buyer/zoho_estimates/',deal_views.zoho_estimates,name='zoho_estimates'),
    path('deals/buyer/zoho_salesorders/',deal_views.zoho_salesorders,name='zoho_salesorders'),
    path('deals/buyer/zoho_estimates/products/',deal_views.estimate_products,name='estimate_products'),
    path('deals/buyer/zoho_estimates/update/',deal_views.update_zoho_estimates,name='update_zoho_estimates'),
    path('deals/buyer/zoho_estimates/update_so',deal_views.update_so,name='update_so'),
    path('deals/buyer/zoho_estimate_inprogress/<int:pk>/',deal_views.zoho_estimate_inprogress,name='zoho_estimate_inprogress'),
    path('deals/buyer/zoho_salesorder_inprogress/<int:pk>/',deal_views.zoho_salesorder_inprogress,name='zoho_salesorder_inprogress'),
    path('deals/buyer/zoho_estimate/<int:pk>/',deal_views.zoho_estimate,name='zoho_estimate'),
    path('deals/buyer/zoho_salesorder/<int:pk>/',deal_views.zoho_salesorder,name='zoho_salesorder'),
    path('deals/buyer/sales_report/',deal_views.sales_report,name='sales_report'),
    path('deals/buyers/salesreport_mail_admin',deal_views.salesreport_mail_admin,name='salesreport_mail_admin'),
    path('ajax/sales_history',deal_views.sales_ajax,name='sales_history_ajax'),
    path('ajax/purchase_history',deal_views.purchase_ajax,name='purchase_history_ajax'),
    path('ajax/recent_deals',deal_views.recent_deals_ajax,name='recent_deals_ajax'),
    path('ajax/graph',deal_views.graph_ajax,name='graph_ajax'),
    path('ajax/coa_view',deal_views.coa_view_ajax,name='coa_view_ajax'),
    path('ajax/coa_delete/<int:pk>/',deal_views.coa_delete_ajax,name='coa_delete_ajax'),
    path('ajax/googlechartsapp',deal_views.googlechartsapp_ajax,name='googlechartsapp_ajax'),

    path('ajax/single-vendor-dealform/',deal_views.single_vendor_dealform,name='single_vendor_dealform'),
    path('ajax/vendor-deal/delete/',deal_views.vendor_deal_delete,name='vendor_deal_delete'),
    path('ajax/vendor-deal/view/',deal_views.vendor_deal_view,name='vendor_deal_view'),
    path('ajax/vendor-deal/edit/',deal_views.vendor_deal_edit,name='vendor_deal_edit'),
    path('ajax/estimate_addproduct_ajax/',deal_views.estimate_addproduct_ajax , name='estimate_addproduct_ajax'),
    path('ajax/estimate_addvendorvariation_ajax/',deal_views.estimate_addvendorvariation_ajax , name='estimate_addvendorvariation_ajax'),
    path('ajax/estimate_updatevendorvariation_ajax/',deal_views.estimate_updatevendorvariation_ajax , name='estimate_updatevendorvariation_ajax'),
    path('ajax/estimate_addvendor_ajax/',deal_views.estimate_addvendor_ajax , name='estimate_addvendor_ajax'),
    path('ajax/estimate-margin/',deal_views.estimate_margin,name="estimate_margin"),
    path('ajax/salesorder_addvendorvariation_ajax/',deal_views.salesorder_addvendorvariation_ajax , name='salesorder_addvendorvariation_ajax'),
    path('ajax/salesorder_updatevendorvariation_ajax/',deal_views.salesorder_updatevendorvariation_ajax , name='salesorder_updatevendorvariation_ajax'),
    path('ajax/salesorder_addvendor_ajax/',deal_views.salesorder_addvendor_ajax , name='salesorder_addvendor_ajax'),
    path('ajax/estimate-margin/',deal_views.estimate_margin,name="estimate_margin"),
    path('ajax/salesorder-margin/',deal_views.salesorder_margin,name="salesorder_margin"),
    path('ajax/relationship_manager_buyers/',deal_views.relationship_manager_buyers,name="relationship_manager_buyers"),
    path('ajax/purchaseorder_pickup/',servicedelivery_views.purchaseorder_pickup,name="purchaseorder_pickup"),
    path('ajax/salesorder_outward/',servicedelivery_views.salesorder_outward,name="salesorder_outward"),
    path('ajax/todays_pickup/',servicedelivery_views.todayspickup,name='todayspickup'),
    path('ajax/todays_dispatch',servicedelivery_views.todaysdispatch,name='todaysdispatch'),
    path('ajax/servicedelivery/inward/dispatchtoday',servicedelivery_views.inward_dispatchtoday,name='inward_dispatchtoday'),
    path('ajax/servicedelivery/inward/dispatchtodaysummary',servicedelivery_views.inward_dispatchtoday_summary,name='inward_dispatchtoday_summary'),
    path('ajax/servicedelivery/inward/receivingtoday',servicedelivery_views.inward_receivingtoday,name='inward_receivingtoday'),
    path('ajax/servicedelivery/inward/receivingtodaysummary',servicedelivery_views.inward_receivingtoday_summary,name='inward_receivingtoday_summary'),
    path('ajax/servicedelivery/outward/previousoutward',servicedelivery_views.previousoutward,name="previousoutward"),
    path('ajax/servicedelivery/outward/nextoutward_dispatch',servicedelivery_views.nextoutward_dispatch,name="nextoutward_dispatch"),
    
    
    path('ajax/salesperson_stats',deal_views.salesperson_stats,name='salesperson_stats'),
    path('ajax/overall_stats',deal_views.overall_stats,name='overall_stats'),
     
    path('salesorder/approve/<int:salesorder_id>',deal_views.salesorder_approve,name="salesorder_approve"),
    path('deals/vendor/list/',deal_views.dealvendor_list,name='deal_vendor_list'),
    path('ajax/payments/payable_pending/get_purchaseorders',payment_views.payable_pending_get_purchaseorders,name="payable_pending_get_purchaseorders"),
    path('payments/payable/pending',payment_views.payments_payable_pending,name = 'payments_payable_pending'),
    path('payments/payable/chequeapproval',payment_views.payments_payable_chequeapproval,name = 'payments_payable_chequeapproval'),
    path('payments/payable/nextpayment',payment_views.payments_payable_nextpayment,name = 'payments_payable_nextpayment'),
    #path('payments/moveup/<int:pk>/',payment_views.payment_moveup,name='payment_moveup'),
    #path('payments/movedown/<int:pk>/',payment_views.payment_movedown,name='payment_movedown'),
    #path('payments/movetop/<int:pk>/',payment_views.payment_movetop,name='payment_movetop'),
    #path('payments/movebottom/<int:pk>/',payment_views.payment_movebottom,name='payment_movebottom'),
    #path('payments/delete/<int:pk>/',payment_views.PaymentDelete.as_view(),name='payment_delete'),
    #path('payments/toggle_check_sent_status/<int:pk>/',payment_views.toggle_check_sent_status,#name='payment_toggle_check_sent_status'),
    ##path('payments/advance/',advancepayment,name='advance_payment'),
    #path('payments/advance/add',payment_views.PaymentCreate.as_view(),name='advance_payment_create'),
    
    
    path('service_delivery/inward/new', servicedelivery_views.inward_servicedelivery_new,name='inward_servicedelivery_new'),
    path('service_delivery/inward/expired', servicedelivery_views.inward_servicedelivery_expired,name='inward_servicedelivery_expired'),
    path('service_delivery/inward/report', servicedelivery_views.inward_servicedelivery_report,name='inward_servicedelivery_report'),
    path('service_delivery/inward/intransit', servicedelivery_views.inward_servicedelivery_intransit,name='inward_servicedelivery_intransit'),
    path('service_delivery/inward/stock', servicedelivery_views.inward_servicedelivery_stock,name='inward_servicedelivery_stock'),
    path('service_delivery/outward', servicedelivery_views.outward_service_delivery, name='outward_servicedelivery'),
    path('service_delivery/outward/shipping', servicedelivery_views.outward_servicedelivery_shipping, name='outward_servicedelivery_shipping'),
    path('service_delivery/outward/intransit', servicedelivery_views.outward_servicedelivery_intransit, name='outward_servicedelivery_intransit'),
    path('service_delivery/outward/report', servicedelivery_views.outward_servicedelivery_report, name='outward_servicedelivery_report'),
    path('service_delivery/report', servicedelivery_views.report_service_delivery, name='report_servicedelivery'),
    path('service_delivery/sendmail_pickup',servicedelivery_views.send_mail_pickup,name='send_mail_pickup'),
    path('service_delivery/sendmail_outward',servicedelivery_views.send_mail_outward,name='send_mail_outward'),
    #path('payments/advance/delete/<int:pk>',AdvancePaymentDelete.as_view(),name='advance_payment_delete'),
    #path('payments/advance/reorder/',advancepayment_reorder,name='advance_payment_reorder'),
    #path('payments/advance/reorder/moveup/<int:pk>/',advancepayment_reorder_moveup,name='advance_payment_reorder_moveup'),
    #path('payments/advance/reorder/movedown/<int:pk>/',advancepayment_reorder_movedown,name='advance_payment_reorder_movedown')
]


urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
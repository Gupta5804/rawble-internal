import django_tables2 as tables
from deals.models import DealVendor
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.html import escape

class DealVendorTable(tables.Table):
    id = tables.Column(verbose_name = 'Deal-ID')
    date = tables.Column()
    time_created = tables.DateTimeColumn(format="M d ,Y ( H:i )")
    edit = tables.TemplateColumn(template_code='<a href="#" data-toggle="modal" data-id="{{ record.id }}" data-target=".edit-{{ record.id }}" class="btn btn-outline-warning btn-sm btn-block js-vendor-deal-edit"> <i class="fas fa-edit"></i> Edit </a> <div class="modal fade edit-{{ record.id }}" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog modal-dialog-centered modal-lg" style="max-width:90%" role="document"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="exampleModalLabel"><i class="fas fa-edit" style="color=yellow;"></i> - Edit Vendor Deal #{{ record.id }}</h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div><div class="modal-body"></div></div></div></div>')
    view = tables.TemplateColumn(template_code='<a href="#" data-toggle="modal" data-id="{{ record.id }}" data-target=".view-{{ record.id }}" class="btn btn-outline-info btn-sm btn-block js-vendor-deal-view"> <i class="fas fa-eye"></i> View </a> <div class="modal fade view-{{ record.id }}" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog modal-dialog-centered modal-lg" style="max-width:90%" role="document"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="exampleModalLabel"><i class="fas fa-user"></i> - Vendor Deal #{{ record.id }}</h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div><div class="modal-body"></div></div></div></div>')
    delete = tables.TemplateColumn(template_code='<a href="#" data-toggle="modal" data-id="{{ record.id }}" data-target=".delete-{{ record.id }}" class="btn btn-outline-danger btn-sm btn-block js-vendor-deal-delete"> <i class="fas fa-trash-alt"></i> Delete </a><div class="modal fade delete-{{ record.id }}" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true"><div class="modal-dialog modal-lg" style="max-width:90%" role="document"><div class="modal-content"><div class="modal-header"><h5 class="modal-title" id="exampleModalLabel"><i class="fas fa-trash"></i> - Delete Vendor Deal #{{ record.id }}</h5><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button></div><div class="modal-body"></div></div></div></div>')
    
    class Meta:
        model = DealVendor
        template_name = 'django_tables2/semantic.html'
    


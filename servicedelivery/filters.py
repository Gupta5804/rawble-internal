from servicedelivery.models import SalesOrderProductPlan
import django_filters
from django_filters import DateFilter , DateRangeFilter , DateFromToRangeFilter ,widgets 
class SOPPFilter(django_filters.FilterSet):
    #date_range = DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD'}))
    date_range = DateRangeFilter(field_name='planned_date_time',label='Duration')
    
    class Meta:
        model = SalesOrderProductPlan
        
        fields = ['salesorderproduct__salesorder__buyer']

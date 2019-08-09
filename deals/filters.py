from deals.models import ZohoSalesOrder
import django_filters
from django_filters import DateFilter,DateRangeFilter,DateFromToRangeFilter,widgetsv
class CustomDateFilter(DateFilter):
    def filter(self, qs, value):
        if value:
            filter_lookups = {
                "%s__month" % (self.field_name, ): value.month,
                "%s__year" % (self.field_name, ): value.year
            }
            qs = qs.filter(**filter_lookups)
        return qs
class SOFilter(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name='date' ,label= 'Select Date Range')
    class Meta:
        model = ZohoSalesOrder
        fields = ['date']
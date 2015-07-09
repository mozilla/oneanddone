import operator
from datetime import datetime

from django import forms
from django.db.models import Q
from django.utils import timezone

from django_filters import CharFilter, Filter

from oneanddone.base.widgets import DateRangeWidget


class DateRangeField(forms.MultiValueField):
    widget = DateRangeWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.DateTimeField(),
            forms.DateTimeField(),
        )
        super(DateRangeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return slice(*data_list)
        return None


# Credit to https://gist.github.com/nkryptic/4727865
class MultiFieldFilter(CharFilter):
    """
    This filter preforms an OR query on the defined fields from a
    single entered value.

    The following will work similar to the default UserAdmin search::

        class UserFilterSet(FilterSet):
            search = MultiFieldFilter(['username', 'first_name',
                                       'last_name', 'email'])
            class Meta:
                model = User
                fields = ['search']
    """

    def __init__(self, fields, *args, **kwargs):
        super(MultiFieldFilter, self).__init__(*args, **kwargs)
        self.fields = fields
        self.lookup_type = 'icontains'
        self.lookup_types = [
            ('^', 'istartswith'),
            ('=', 'iexact'),
            ('@', 'search'),
        ]

    def filter(self, qs, value):
        if not self.fields or not value:
            return qs

        lookups = [self._get_lookup(str(field)) for field in self.fields]
        queries = [Q(**{lookup: value}) for lookup in lookups]
        qs = qs.filter(reduce(operator.or_, queries))
        return qs.distinct()

    def _get_lookup(self, field_name):
        for key, lookup_type in self.lookup_types:
            if field_name.startswith(key):
                return "%s__%s" % (field_name[len(key):], lookup_type)
        return "%s__%s" % (field_name, self.lookup_type)


class MyDateRangeFilter(Filter):
    field_class = DateRangeField

    def filter(self, qs, value):
        if value:
            lookup = '%s__range' % self.name
            start = value.start or timezone.make_aware(
                datetime(2013, 1, 1), timezone.utc)
            stop = value.stop or timezone.now()
            return qs.filter(**{lookup: (start, stop)})
        return qs

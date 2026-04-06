from django_admin_boost.unfold.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from django_admin_boost.unfold.contrib.filters.admin.mixins import AutocompleteMixin
from django_admin_boost.unfold.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(AutocompleteMixin, RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm


class AutocompleteSelectMultipleFilter(
    AutocompleteMixin, MultipleRelatedDropdownFilter,
):
    form_class = AutocompleteDropdownForm

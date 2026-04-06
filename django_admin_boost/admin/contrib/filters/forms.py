from __future__ import annotations

from django import forms
from django.conf import settings
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.widgets import (
    AdminRadioSelect,
    AdminSplitDateTime,
    AdminTextInputWidget,
    AutocompleteSelect,
    AutocompleteSelectMultiple,
)
from django.db.models import Field as ModelField
from django.forms import (
    CheckboxSelectMultiple,
    ChoiceField,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    Select,
    SelectMultiple,
)
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


class SearchForm(forms.Form):
    def __init__(self, name: str, label: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.CharField(
            label=label,
            required=False,
            widget=AdminTextInputWidget,
        )


class AutocompleteDropdownForm(forms.Form):
    field = forms.ModelChoiceField
    widget = AutocompleteSelect

    def __init__(
        self,
        request: HttpRequest,
        name: str,
        label: str,
        choices: tuple,
        field: ModelField,
        model_admin: ModelAdmin,
        multiple: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if multiple:
            self.field = ModelMultipleChoiceField
            self.widget = AutocompleteSelectMultiple

        self.fields[name] = self.field(
            label=label,
            required=False,
            queryset=field.remote_field.model.objects,
            widget=self.widget(
                field,
                model_admin.admin_site,
            ),
        )

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "admin/contrib/filters/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class CheckboxForm(forms.Form):
    field = MultipleChoiceField
    widget = CheckboxSelectMultiple

    def __init__(
        self,
        name: str,
        label: str,
        choices: tuple | list,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fields[name] = self.field(
            label=label,
            required=False,
            choices=choices,
            widget=self.widget,
        )


class RadioForm(CheckboxForm):
    field = ChoiceField
    widget = AdminRadioSelect


class HorizontalRadioForm(RadioForm):
    widget = AdminRadioSelect


class DropdownForm(forms.Form):
    widget = Select
    field = ChoiceField

    def __init__(
        self,
        name: str,
        label: str,
        choices: tuple,
        multiple: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        widget = self.widget
        field = self.field

        if multiple:
            widget = SelectMultiple
            field = MultipleChoiceField

        self.fields[name] = field(
            label=label,
            required=False,
            choices=choices,
            widget=widget,
        )

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "admin/contrib/filters/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class SingleNumericForm(forms.Form):
    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("Value")}),
        )


class RangeNumericForm(forms.Form):
    def __init__(
        self,
        name: str,
        min: float | None = None,
        max: float | None = None,
        *args,
        **kwargs,
    ) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        min_max = {}
        if min:
            min_max["min"] = min
        if max:
            min_max["max"] = max

        self.fields[self.name + "_from"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("From"), **min_max}),
        )
        self.fields[self.name + "_to"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("To"), **min_max}),
        )


class SliderNumericForm(RangeNumericForm):
    class Media:
        css = {"all": ("admin/contrib/filters/css/nouislider/nouislider.min.css",)}
        js = (
            "admin/contrib/filters/js/wnumb/wNumb.min.js",
            "admin/contrib/filters/js/nouislider/nouislider.min.js",
            "admin/contrib/filters/js/admin-numeric-filter.js",
        )


class RangeDateForm(forms.Form):
    class Media:
        js = [
            "admin/js/calendar.js",
            "admin/contrib/filters/js/DateTimeShortcuts.js",
        ]

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.DateField(
            label="",
            required=False,
            widget=forms.DateInput(
                attrs={"placeholder": _("From"), "class": "vCustomDateField"},
            ),
        )
        self.fields[self.name + "_to"] = forms.DateField(
            label="",
            required=False,
            widget=forms.DateInput(
                attrs={"placeholder": _("To"), "class": "vCustomDateField"},
            ),
        )


class RangeDateTimeForm(forms.Form):
    class Media:
        js = [
            "admin/js/calendar.js",
            "admin/contrib/filters/js/DateTimeShortcuts.js",
        ]

    def __init__(self, name: str, *args, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_from"] = forms.SplitDateTimeField(
            label="",
            required=False,
            widget=AdminSplitDateTime(
                attrs={
                    "placeholder": _("Date from"),
                    "class": "vCustomDateField",
                },
            ),
        )
        self.fields[self.name + "_to"] = forms.SplitDateTimeField(
            label="",
            required=False,
            widget=AdminSplitDateTime(
                attrs={
                    "placeholder": _("Date to"),
                    "class": "vCustomDateField",
                },
            ),
        )

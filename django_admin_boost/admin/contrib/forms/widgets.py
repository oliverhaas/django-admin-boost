from __future__ import annotations

from typing import Any

from django.contrib.admin.widgets import AdminTextInputWidget
from django.core.validators import EMPTY_VALUES
from django.forms import MultiWidget, Select, Widget
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict


class ArrayWidget(MultiWidget):
    template_name = "admin/forms/array.html"

    def __init__(
        self,
        widget_class: type[Widget] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.choices = kwargs.get("choices")
        self.widget_class = widget_class

        widgets = [self.get_widget_instance()]
        super().__init__(widgets, attrs=kwargs.get("attrs", None))

    def get_widget_instance(self) -> Any:
        if hasattr(self, "widget_class") and self.widget_class is not None:
            return self.widget_class()

        if hasattr(self, "choices") and self.choices is not None:
            return Select(choices=self.choices)

        return AdminTextInputWidget()

    def get_context(self, name: str, value: Any, attrs: dict | None) -> dict:
        self._resolve_widgets(value)
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "template": self.get_widget_instance().get_context(name, "", {})[
                    "widget"
                ],
            },
        )
        return context

    def value_from_datadict(
        self,
        data: QueryDict,
        files: MultiValueDict,
        name: str,
    ) -> list:
        values = []

        for item in data.getlist(name):
            if item not in EMPTY_VALUES:
                values.append(item)

        return values

    def value_omitted_from_data(
        self,
        data: QueryDict,
        files: MultiValueDict,
        name: str,
    ) -> bool:
        return data.getlist(name) not in [[""], *EMPTY_VALUES]

    def decompress(self, value: Any) -> list:
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return value.split(",")

        return []

    def _resolve_widgets(self, value: list | str | None) -> None:
        if value is None:
            value = []
        elif isinstance(value, list):
            self.widgets = [self.get_widget_instance() for item in value]
        else:
            self.widgets = [self.get_widget_instance() for item in value.split(",")]

        self.widgets_names = ["" for i in range(len(self.widgets))]
        self.widgets = [w if isinstance(w, type) else w for w in self.widgets]


class WysiwygWidget(Widget):
    template_name = "admin/forms/wysiwyg.html"

    class Media:
        css = {"all": ("admin/contrib/forms/css/trix/trix.css",)}
        js = (
            "admin/contrib/forms/js/trix/trix.js",
            "admin/contrib/forms/js/trix.config.js",
        )

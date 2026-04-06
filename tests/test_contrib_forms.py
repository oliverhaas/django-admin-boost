from django.test import TestCase


class ArrayWidgetTest(TestCase):
    def test_decompress_list(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        assert widget.decompress(["a", "b"]) == ["a", "b"]

    def test_decompress_csv_string(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        assert widget.decompress("a,b,c") == ["a", "b", "c"]

    def test_decompress_none(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        assert widget.decompress(None) == []

    def test_value_from_datadict_filters_empty(self) -> None:
        from django.http import QueryDict

        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget()
        data = QueryDict(mutable=True)
        data.setlist("tags", ["foo", "", "bar"])
        result = widget.value_from_datadict(data, {}, "tags")
        assert result == ["foo", "bar"]

    def test_custom_widget_class(self) -> None:
        from django.forms import NumberInput

        from django_admin_boost.admin.contrib.forms.widgets import ArrayWidget

        widget = ArrayWidget(widget_class=NumberInput)
        instance = widget.get_widget_instance()
        assert isinstance(instance, NumberInput)


class WysiwygWidgetTest(TestCase):
    def test_template_name(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import WysiwygWidget

        widget = WysiwygWidget()
        assert widget.template_name == "admin/forms/wysiwyg.html"

    def test_media_includes_trix(self) -> None:
        from django_admin_boost.admin.contrib.forms.widgets import WysiwygWidget

        widget = WysiwygWidget()
        media_str = str(widget.media)
        assert "trix.js" in media_str
        assert "trix.css" in media_str

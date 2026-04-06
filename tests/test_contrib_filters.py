import datetime

from django.contrib.admin import site as admin_site
from django.contrib.admin.widgets import AdminRadioSelect, AdminSplitDateTime
from django.contrib.auth.models import User
from django.forms import CheckboxSelectMultiple, Select
from django.test import RequestFactory, TestCase, override_settings

from tests.testapp.models import Article


class ParseDateStrTest(TestCase):
    def test_parses_iso_format(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_date_str

        result = parse_date_str("2026-01-15")
        assert result == datetime.date(2026, 1, 15)

    def test_returns_none_for_invalid(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_date_str

        result = parse_date_str("not-a-date")
        assert result is None

    @override_settings(DATE_INPUT_FORMATS=["%d/%m/%Y", "%Y-%m-%d"])
    def test_uses_settings_formats(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_date_str

        result = parse_date_str("15/01/2026")
        assert result == datetime.date(2026, 1, 15)


class ParseDateTimeStrTest(TestCase):
    def test_parses_iso_format(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_datetime_str

        result = parse_datetime_str("2026-01-15 10:30:00")
        assert result == datetime.datetime(2026, 1, 15, 10, 30, 0)  # noqa: DTZ001

    def test_returns_none_for_invalid(self) -> None:
        from django_admin_boost.admin.contrib.filters.utils import parse_datetime_str

        result = parse_datetime_str("not-a-datetime")
        assert result is None


class SearchFormTest(TestCase):
    def test_creates_text_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import SearchForm

        form = SearchForm(name="q", label="Search", data={"q": "test"})
        assert "q" in form.fields
        assert form.fields["q"].required is False


class CheckboxFormTest(TestCase):
    def test_creates_multiple_choice_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import CheckboxForm

        form = CheckboxForm(
            name="status",
            label="By status",
            choices=[("draft", "Draft"), ("published", "Published")],
            data={"status": ["draft"]},
        )
        assert "status" in form.fields
        assert isinstance(form.fields["status"].widget, CheckboxSelectMultiple)


class RadioFormTest(TestCase):
    def test_creates_choice_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RadioForm

        form = RadioForm(
            name="status",
            label="By status",
            choices=[("", "All"), ("draft", "Draft")],
            data={"status": ""},
        )
        assert "status" in form.fields
        assert isinstance(form.fields["status"].widget, AdminRadioSelect)


class DropdownFormTest(TestCase):
    def test_creates_select_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import DropdownForm

        form = DropdownForm(
            name="category",
            label="By category",
            choices=[("", "All"), ("1", "News")],
            data={"category": ""},
        )
        assert "category" in form.fields
        assert isinstance(form.fields["category"].widget, Select)


class RangeNumericFormTest(TestCase):
    def test_creates_from_and_to_fields(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RangeNumericForm

        form = RangeNumericForm(name="price", data={})
        assert "price_from" in form.fields
        assert "price_to" in form.fields


class SingleNumericFormTest(TestCase):
    def test_creates_numeric_field(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import SingleNumericForm

        form = SingleNumericForm(name="priority", data={})
        assert "priority" in form.fields


class RangeDateFormTest(TestCase):
    def test_creates_date_from_and_to(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RangeDateForm

        form = RangeDateForm(name="publish_date", data={})
        assert "publish_date_from" in form.fields
        assert "publish_date_to" in form.fields


class RangeDateTimeFormTest(TestCase):
    def test_creates_datetime_from_and_to(self) -> None:
        from django_admin_boost.admin.contrib.filters.forms import RangeDateTimeForm

        form = RangeDateTimeForm(name="created_at", data={})
        assert "created_at_from" in form.fields
        assert "created_at_to" in form.fields
        assert isinstance(form.fields["created_at_from"].widget, AdminSplitDateTime)


class ValueMixinTest(TestCase):
    def test_returns_first_item_from_list(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import ValueMixin

        obj = ValueMixin()
        obj.lookup_val = ["foo", "bar"]
        assert obj.value() == "foo"

    def test_returns_none_when_no_value(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import ValueMixin

        obj = ValueMixin()
        obj.lookup_val = None
        assert obj.value() is None


class MultiValueMixinTest(TestCase):
    def test_returns_list(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import MultiValueMixin

        obj = MultiValueMixin()
        obj.lookup_val = ["foo", "bar"]
        assert obj.value() == ["foo", "bar"]


class RangeNumericMixinTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Cheap", priority=10)
        Article.objects.create(title="Expensive", priority=90)

    def test_filters_queryset_by_range(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import RangeNumericMixin

        mixin = RangeNumericMixin.__new__(RangeNumericMixin)
        mixin.parameter_name = "priority"
        mixin.used_parameters = {"priority_from": "10", "priority_to": "50"}
        qs = Article.objects.all()
        result = mixin.queryset(None, qs)
        assert result.count() == 1
        assert result.first().title == "Cheap"

    def test_expected_parameters(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.mixins import RangeNumericMixin

        mixin = RangeNumericMixin.__new__(RangeNumericMixin)
        mixin.parameter_name = "priority"
        assert mixin.expected_parameters() == ["priority_from", "priority_to"]


class TextFilterTest(TestCase):
    def test_has_output_returns_true(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin.text_filters import TextFilter

        class TitleFilter(TextFilter):
            title = "Title"
            parameter_name = "title__icontains"

            def lookups(self, request, model_admin):
                return ()

            def queryset(self, request, queryset):
                if self.value():
                    return queryset.filter(title__icontains=self.value())
                return queryset

        f = TitleFilter(None, {}, Article, None)
        assert f.has_output() is True


class FieldTextFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Hello World")
        Article.objects.create(title="Goodbye World")
        cls.superuser = User.objects.create_superuser(
            username="admin_text",
            password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_by_icontains(self) -> None:
        from django_admin_boost.admin import ModelAdmin
        from django_admin_boost.admin.contrib.filters.admin.text_filters import FieldTextFilter

        class ArticleAdmin(ModelAdmin):
            list_filter = [("title", FieldTextFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get(
            "/admin/testapp/article/",
            {"title__icontains": "Hello"},
        )
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Hello World"


class RangeNumericFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Low", priority=5)
        Article.objects.create(title="Mid", priority=50)
        Article.objects.create(title="High", priority=95)
        cls.superuser = User.objects.create_superuser(
            username="admin_numeric",
            password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_by_range(self) -> None:
        from django_admin_boost.admin import ModelAdmin
        from django_admin_boost.admin.contrib.filters.admin.numeric_filters import (
            RangeNumericFilter,
        )

        class ArticleAdmin(ModelAdmin):
            list_filter = [("priority", RangeNumericFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get(
            "/admin/testapp/article/",
            {"priority_from": "10", "priority_to": "60"},
        )
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Mid"


class SingleNumericFilterTest2(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Target", priority=42)
        Article.objects.create(title="Other", priority=99)
        cls.superuser = User.objects.create_superuser(
            username="admin_single",
            password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_exact(self) -> None:
        from django_admin_boost.admin import ModelAdmin
        from django_admin_boost.admin.contrib.filters.admin.numeric_filters import (
            SingleNumericFilter,
        )

        class ArticleAdmin(ModelAdmin):
            list_filter = [("priority", SingleNumericFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get("/admin/testapp/article/", {"priority": "42"})
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Target"


class RangeDateFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Article.objects.create(title="Old", publish_date=datetime.date(2025, 1, 1))
        Article.objects.create(title="Recent", publish_date=datetime.date(2026, 3, 15))
        Article.objects.create(title="Future", publish_date=datetime.date(2027, 6, 1))
        cls.superuser = User.objects.create_superuser(
            username="admin_date",
            password="password",
        )

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_filters_by_date_range(self) -> None:
        from django_admin_boost.admin import ModelAdmin
        from django_admin_boost.admin.contrib.filters.admin.datetime_filters import (
            RangeDateFilter,
        )

        class ArticleAdmin(ModelAdmin):
            list_filter = [("publish_date", RangeDateFilter)]

        ma = ArticleAdmin(Article, admin_site)
        request = self.factory.get(
            "/admin/testapp/article/",
            {"publish_date_from": "2026-01-01", "publish_date_to": "2026-12-31"},
        )
        request.user = self.superuser
        changelist = ma.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        assert qs.count() == 1
        assert qs.first().title == "Recent"


class FilterImportsTest(TestCase):
    def test_all_filters_importable(self) -> None:
        from django_admin_boost.admin.contrib.filters.admin import (
            AutocompleteSelectFilter,
            AutocompleteSelectMultipleFilter,
            BooleanRadioFilter,
            DropdownFilter,
            FieldTextFilter,
            RadioFilter,
            RangeDateFilter,
            RangeDateTimeFilter,
            RangeNumericFilter,
            SingleNumericFilter,
            SliderNumericFilter,
            TextFilter,
        )

        assert all(
            [
                TextFilter,
                FieldTextFilter,
                RadioFilter,
                BooleanRadioFilter,
                RangeDateFilter,
                RangeDateTimeFilter,
                SingleNumericFilter,
                RangeNumericFilter,
                SliderNumericFilter,
                DropdownFilter,
                AutocompleteSelectFilter,
                AutocompleteSelectMultipleFilter,
            ],
        )

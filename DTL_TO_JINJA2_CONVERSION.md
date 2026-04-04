# DTL → Jinja2 Conversion Reference

Comprehensive mapping of every Django Template Language construct to its Jinja2 equivalent, based on converting all 50 Django admin templates.

## Tag Conversions

### Loading
```
DTL:    {% load i18n static admin_list %}
Jinja2: (removed — extensions/globals are registered in the environment)
```

### Translation
```
DTL:    {% translate 'Home' %}
Jinja2: {{ gettext('Home') }}

DTL:    {% trans "Home" %}
Jinja2: {{ gettext("Home") }}

DTL:    {% blocktranslate with name=app.name %}Models in {{ name }}{% endblocktranslate %}
Jinja2: {% trans name=app.name %}Models in {{ name }}{% endtrans %}

DTL:    {% blocktranslate count counter=items|length %}One item{% plural %}{{ counter }} items{% endblocktranslate %}
Jinja2: {% trans count=items|length %}One item{% pluralize %}{{ count }} items{% endtrans %}
        (note: Jinja2 uses `count` not `counter` in the plural block)

DTL:    {% blocktranslate trimmed %}...{% endblocktranslate %}
Jinja2: {% trans %}...{% endtrans %}
        (Jinja2 trans blocks trim whitespace by default)

DTL:    {% blocktranslate trimmed context "some context" %}...{% endblocktranslate %}
Jinja2: {% trans context "some context" %}...{% endtrans %}
```

### URLs
```
DTL:    {% url 'admin:index' %}
Jinja2: {{ url('admin:index') }}

DTL:    {% url 'admin:app_list' app_label=cl.opts.app_label %}
Jinja2: {{ url('admin:app_list', app_label=cl.opts.app_label) }}

DTL:    {% url 'admin:password_change' as password_url %}
Jinja2: {% set password_url = url('admin:password_change', silent=True) %}
        (silent=True catches NoReverseMatch and returns "")

DTL:    {% url opts|admin_urlname:'changelist' %}
Jinja2: {{ url(opts|admin_urlname('changelist')) }}
```

### Static Files
```
DTL:    {% static "admin/css/base.css" %}
Jinja2: {{ static('admin/css/base.css') }}
```

### CSRF
```
DTL:    {% csrf_token %}
Jinja2: {{ csrf_input }}
        (injected by Django's Jinja2 backend automatically)
```

### Template Inheritance
```
DTL:    {% extends "admin/base.html" %}
Jinja2: {% extends "admin/base.html" %}  (same)

DTL:    {% block content %}...{% endblock %}
Jinja2: {% block content %}...{% endblock %}  (same)

DTL:    {{ block.super }}
Jinja2: {{ super() }}
```

### Includes
```
DTL:    {% include "admin/app_list.html" %}
Jinja2: {% include "admin/app_list.html" %}  (same)

DTL:    {% include "admin/app_list.html" with show_changelinks=True %}
Jinja2: {% set show_changelinks = True %}
        {% include "admin/app_list.html" %}
        (Jinja2 include passes full context; set variables before include)

DTL:    {% include "admin/app_list.html" with show_changelinks=True only %}
Jinja2: {% set show_changelinks = True %}
        {% include "admin/app_list.html" %}
        (no direct equivalent for `only`; variables leak into parent scope)
```

### Control Flow
```
DTL:    {% for item in items %}...{% empty %}Nothing{% endfor %}
Jinja2: {% for item in items %}...{% else %}Nothing{% endfor %}

DTL:    {% if x %}...{% elif y %}...{% else %}...{% endif %}
Jinja2: {% if x %}...{% elif y %}...{% else %}...{% endif %}  (same)

DTL:    {% with name=value %}...{% endwith %}
Jinja2: {% set name = value %}
        (no block scoping — variable persists in current scope)
```

### Loop Variables
```
DTL:    {{ forloop.counter }}     → Jinja2: {{ loop.index }}      (1-based)
DTL:    {{ forloop.counter0 }}    → Jinja2: {{ loop.index0 }}     (0-based)
DTL:    {{ forloop.last }}        → Jinja2: {{ loop.last }}
DTL:    {{ forloop.first }}       → Jinja2: {{ loop.first }}
DTL:    {{ forloop.revcounter }}  → Jinja2: {{ loop.revindex }}
DTL:    {{ forloop.revcounter0 }} → Jinja2: {{ loop.revindex0 }}
```

### Other Tags
```
DTL:    {% now "Z" %}
Jinja2: {{ now("Z") }}
        (custom global wrapping django.utils.dateformat.format)

DTL:    {% firstof user.get_short_name user.get_username %}
Jinja2: {{ user.get_short_name() or user.get_username() }}
        (note: must call methods with ())

DTL:    {% cycle 'row1' 'row2' %}
Jinja2: {{ loop.cycle('row1', 'row2') }}
        (only works inside a for loop)

DTL:    {% spaceless %}...{% endspaceless %}
Jinja2: (remove tag; use {%- -%} trim markers for tight whitespace)

DTL:    {% filter capfirst %}{{ value }}{% endfilter %}
Jinja2: {{ value|capfirst }}

DTL:    {% get_current_language as LANGUAGE_CODE %}
Jinja2: {% set LANGUAGE_CODE = get_current_language() %}

DTL:    {% get_current_language_bidi as LANGUAGE_BIDI %}
Jinja2: {% set LANGUAGE_BIDI = get_current_language_bidi() %}

DTL:    {% autoescape off %}...{% endautoescape %}
Jinja2: {% autoescape false %}...{% endautoescape %}
```

## Filter Conversions

```
DTL:    {{ value|default:"fallback" }}
Jinja2: {{ value|default("fallback") }}

DTL:    {{ value|default_if_none:"fallback" }}
Jinja2: {{ value if value is not none else "fallback" }}

DTL:    {{ value|yesno:"Yes,No,Maybe" }}
Jinja2: {{ value|yesno("Yes,No,Maybe") }}
        (custom filter)

DTL:    {{ value|capfirst }}
Jinja2: {{ value|capfirst }}  (custom filter wrapping django.utils.text.capfirst)

DTL:    {{ value|truncatewords:10 }}
Jinja2: {{ value|truncatewords(10) }}  (custom filter)

DTL:    {{ value|date:"DATE_FORMAT" }}
Jinja2: {{ value|date("DATE_FORMAT") }}  (custom filter)

DTL:    {{ value|length }}
Jinja2: {{ value|length }}  (same)

DTL:    {{ value|length_is:"1" }}
Jinja2: {{ value|length == 1 }}

DTL:    {{ value|stringformat:"s" }}
Jinja2: {{ value|string }}

DTL:    {{ value|urlencode }}
Jinja2: {{ value|urlencode_path }}  (custom filter)

DTL:    {{ value|unordered_list }}
Jinja2: {{ value|unordered_list }}  (custom filter)

DTL:    {{ value|safe }}
Jinja2: {{ value|safe }}  (same)

DTL:    {{ opts|admin_urlname:'changelist' }}
Jinja2: {{ opts|admin_urlname('changelist') }}
        (filter takes argument via function call syntax)

DTL:    {{ value|admin_urlquote }}
Jinja2: {{ value|admin_urlquote }}  (same, custom filter)

DTL:    {{ inline_admin_form|cell_count }}
Jinja2: {{ inline_admin_form|cell_count }}  (custom filter)

DTL:    {{ value|unlocalize }}
Jinja2: {{ value|unlocalize }}  (custom filter)
```

## Admin-Specific: Inclusion Tags → Globals + Include

The hardest conversion. Django admin uses `InclusionAdminNode` — tags that call a Python function, get a dict, then render a sub-template with that dict as context.

### Pattern
```
DTL:    {% load admin_list %}
        {% result_list cl %}

Jinja2: {% set _ctx = result_list(cl) %}
        {% set result_hidden_fields_list = _ctx.result_hidden_fields %}
        {% set num_sorted_fields = _ctx.num_sorted_fields %}
        {% set results_list = _ctx.results %}
        {% set headers = _ctx.headers %}
        {% include "admin/change_list_results.html" %}
```

### All Inclusion Tags

| DTL Tag | Jinja2 Global | Sub-template |
|---------|---------------|--------------|
| `{% result_list cl %}` | `result_list(cl)` | `change_list_results.html` |
| `{% pagination cl %}` | `pagination(cl)` | `pagination.html` |
| `{% search_form cl %}` | `search_form(cl)` | `search_form.html` |
| `{% date_hierarchy cl %}` | `date_hierarchy(cl)` | `date_hierarchy.html` |
| `{% admin_actions %}` | `admin_actions(context)` | `actions.html` |
| `{% change_list_object_tools %}` | (inline in template) | `change_list_object_tools.html` |
| `{% submit_row %}` | `submit_row(context)` | `submit_line.html` |
| `{% prepopulated_fields_js %}` | `prepopulated_fields_js(context)` | `prepopulated_fields_js.html` |
| `{% change_form_object_tools %}` | (inline in template) | `change_form_object_tools.html` |

### Template Override Hierarchy

DTL's `InclusionAdminNode` resolves templates via 3-level lookup:
```
admin/{app_label}/{model_name}/{template_name}
admin/{app_label}/{template_name}
admin/{template_name}
```

In Jinja2, use the `select_admin_template()` helper with `{% include %}`:
```jinja2
{% include select_admin_template(opts, "change_list_results.html") %}
```
Jinja2's `{% include %}` accepts a list and uses the first template found.

### Simple Tags → Global Functions

```
DTL:    {% paginator_number cl i %}
Jinja2: {{ paginator_number(cl, i) }}

DTL:    {% admin_list_filter cl spec %}
Jinja2: {{ admin_list_filter(cl, spec) }}

DTL:    {% add_preserved_filters url %}
Jinja2: {{ add_preserved_filters(url) }}
```

### Admin Log Tag

```
DTL:    {% load log %}
        {% get_admin_log 10 as admin_log for_user user %}

Jinja2: {% set admin_log = get_admin_log(10, user) %}
```

## Jinja2 Environment Requirements

The Jinja2 environment must register:

**Extension:** `jinja2.ext.i18n` with `install_gettext_callables(gettext, ngettext, newstyle=True)`

**Globals:** `static`, `url`, `now`, `get_current_language`, `get_current_language_bidi`, `get_admin_log`, `select_admin_template`, `result_list`, `result_headers`, `results`, `result_hidden_fields`, `pagination`, `paginator_number`, `search_form`, `date_hierarchy`, `admin_list_filter`, `admin_actions`, `submit_row`, `prepopulated_fields_js`, `add_preserved_filters`

**Filters:** `capfirst`, `yesno`, `admin_urlname`, `admin_urlquote`, `urlencode_path`, `cell_count`, `date`, `truncatewords`, `unlocalize`, `unordered_list`

**Injected by Django's Jinja2 backend (not in environment):** `csrf_input`, `csrf_token`, `request`, context processor output

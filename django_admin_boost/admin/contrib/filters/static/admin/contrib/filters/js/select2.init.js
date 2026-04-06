document.addEventListener("DOMContentLoaded", function () {
    if (typeof django !== "undefined" && typeof django.jQuery !== "undefined") {
        django.jQuery(".admin-autocomplete").not("[name*=__prefix__]").select2();
    }
});

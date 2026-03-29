from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(default="")
    status = models.CharField(max_length=20, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "testapp"

    def __str__(self) -> str:
        return self.title

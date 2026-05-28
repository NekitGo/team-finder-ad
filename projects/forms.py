from django import forms

from core.mixins import GithubUrlMixin
from projects.models import Project


class ProjectForm(GithubUrlMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "status": forms.Select(choices=[("open", "Открыт"), ("closed", "Закрыт")]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["github_url"].required = False

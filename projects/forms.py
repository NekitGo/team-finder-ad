from django import forms

from projects.models import Project

GITHUB_DOMAIN = "github.com"


def validate_github_url(value):
    if value and GITHUB_DOMAIN not in value:
        raise forms.ValidationError("Ссылка должна вести на GitHub.")


class ProjectForm(forms.ModelForm):
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

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url:
            validate_github_url(url)
        return url

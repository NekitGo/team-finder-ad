from django import forms

from core.validators import validate_github_url


class GithubUrlMixin(forms.Form):
    """Adds GitHub URL validation to any ModelForm that has a github_url field."""

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url:
            validate_github_url(url)
        return url

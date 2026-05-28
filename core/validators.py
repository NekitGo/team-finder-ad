from django.core.exceptions import ValidationError

GITHUB_DOMAIN = "github.com"


def validate_github_url(value):
    if value and GITHUB_DOMAIN not in value:
        raise ValidationError("Ссылка должна вести на GitHub.")

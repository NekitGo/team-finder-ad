import io
import random

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)
from users.constants import AVATAR_FONT_PATH, AVATAR_FONT_RATIO, AVATAR_SIZE, AVATAR_TEXT_COLOR, AvatarColor
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=USER_PHONE_MAX_LENGTH, blank=True, default="")
    github_url = models.URLField(blank=True, default="")
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.pk is None and not self.avatar:
            avatar_image = self._create_avatar_image()
            filename = f"avatar_{self.email.split('@')[0]}.png"
            self.avatar.save(filename, avatar_image, save=False)
        super().save(*args, **kwargs)

    def _create_avatar_image(self) -> ContentFile:
        color = random.choice(list(AvatarColor))
        letter = (self.name[0] if self.name else "?").upper()
        font_size = int(AVATAR_SIZE * AVATAR_FONT_RATIO)

        img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(str(AVATAR_FONT_PATH), size=font_size)
        except (IOError, OSError):
            font = ImageFont.load_default(size=font_size)

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (AVATAR_SIZE - text_w) / 2 - bbox[0]
        y = (AVATAR_SIZE - text_h) / 2 - bbox[1]
        draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return ContentFile(buffer.read())

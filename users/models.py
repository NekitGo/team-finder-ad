import io
import random

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    "#4A90D9", "#5BA85A", "#D47A3A", "#8B6BB1",
    "#C75B5B", "#4AADAD", "#C0934A", "#7B8CBF",
]


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=12, blank=True, default="")
    github_url = models.URLField(blank=True, default="")
    about = models.TextField(max_length=256, blank=True, default="")
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.avatar:
            avatar_image = self._create_avatar_image()
            filename = f"avatar_{self.email.split('@')[0]}.png"
            self.avatar.save(filename, avatar_image, save=False)
        super().save(*args, **kwargs)

    def _create_avatar_image(self):
        size = 200
        color = random.choice(AVATAR_COLORS)
        letter = (self.name[0] if self.name else "?").upper()

        img = Image.new("RGB", (size, size), color=color)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(
                "/Users/nekitf/Documents/team-finder-ad/static/fonts/Neue_Haas_Grotesk_Display_Pro_75_Bold.otf",
                size=100,
            )
        except (IOError, OSError):
            font = ImageFont.load_default(size=100)

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) / 2 - bbox[0]
        y = (size - text_h) / 2 - bbox[1]
        draw.text((x, y), letter, fill="white", font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return ContentFile(buffer.read())

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project

User = get_user_model()

USERS = [
    {
        "email": "admin@teamfinder.ru",
        "name": "Admin",
        "surname": "Adminov",
        "password": "adminpass123",
        "is_staff": True,
        "is_superuser": True,
        "about": "Администратор платформы TeamFinder.",
        "phone": "+79001234567",
    },
    {
        "email": "maria@yandex.ru",
        "name": "Мария",
        "surname": "Иванова",
        "password": "password",
        "about": "Full-stack разработчик, люблю Python и Vue.js.",
        "phone": "+79001234568",
        "github_url": "https://github.com/maria",
    },
    {
        "email": "alex@gmail.com",
        "name": "Александр",
        "surname": "Петров",
        "password": "password123",
        "about": "Backend разработчик, специалист по Django и FastAPI.",
        "phone": "+79001234569",
        "github_url": "https://github.com/alex",
    },
    {
        "email": "anna@mail.ru",
        "name": "Анна",
        "surname": "Смирнова",
        "password": "password123",
        "about": "UI/UX дизайнер и фронтенд разработчик.",
        "phone": "+79001234570",
    },
    {
        "email": "ivan@yandex.ru",
        "name": "Иван",
        "surname": "Козлов",
        "password": "password123",
        "about": "Data Scientist, работаю с ML и анализом данных.",
        "phone": "+79001234571",
        "github_url": "https://github.com/ivan",
    },
]

PROJECTS = [
    {
        "owner_email": "maria@yandex.ru",
        "name": "TeamFinder Platform",
        "description": (
            "Платформа для поиска участников в pet-проекты. "
            "Разработчики, дизайнеры и другие специалисты могут "
            "находить единомышленников для совместной работы."
        ),
        "status": "open",
        "github_url": "https://github.com/maria/team-finder",
    },
    {
        "owner_email": "maria@yandex.ru",
        "name": "Open Source Task Manager",
        "description": "Менеджер задач с открытым исходным кодом, построенный на Django и React.",
        "status": "open",
    },
    {
        "owner_email": "alex@gmail.com",
        "name": "API Gateway Microservice",
        "description": (
            "Высокопроизводительный API шлюз для микросервисной архитектуры "
            "на Python с поддержкой WebSocket и gRPC."
        ),
        "status": "open",
        "github_url": "https://github.com/alex/api-gateway",
    },
    {
        "owner_email": "alex@gmail.com",
        "name": "Crypto Portfolio Tracker",
        "description": "Трекер криптовалютного портфеля с уведомлениями и аналитикой.",
        "status": "closed",
    },
    {
        "owner_email": "anna@mail.ru",
        "name": "Design System Library",
        "description": (
            "Библиотека компонентов дизайн-системы для быстрой разработки "
            "интерфейсов с поддержкой тёмной темы."
        ),
        "status": "open",
    },
    {
        "owner_email": "anna@mail.ru",
        "name": "Portfolio Builder",
        "description": "Конструктор портфолио для дизайнеров с красивыми шаблонами.",
        "status": "open",
        "github_url": "https://github.com/anna/portfolio-builder",
    },
    {
        "owner_email": "ivan@yandex.ru",
        "name": "ML Model Marketplace",
        "description": (
            "Маркетплейс для обмена и монетизации ML-моделей. "
            "Позволяет загружать, тестировать и использовать чужие модели через API."
        ),
        "status": "open",
        "github_url": "https://github.com/ivan/ml-marketplace",
    },
    {
        "owner_email": "ivan@yandex.ru",
        "name": "Natural Language SQL Query",
        "description": (
            "Инструмент для генерации SQL запросов из естественного языка "
            "с использованием больших языковых моделей."
        ),
        "status": "open",
    },
]


class Command(BaseCommand):
    help = "Seed the database with test users and projects"

    def handle(self, *args, **options):
        self.stdout.write("Creating test users...")
        created_users = {}
        for data in USERS:
            email = data["email"]
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                self.stdout.write(f"  User {email} already exists, skipping.")
            else:
                kwargs = {
                    k: v for k, v in data.items()
                    if k not in ("email", "password", "name", "surname")
                }
                user = User.objects.create_user(
                    email=email,
                    name=data["name"],
                    surname=data["surname"],
                    password=data["password"],
                    **kwargs,
                )
                self.stdout.write(f"  Created user: {email}")
            created_users[email] = user

        self.stdout.write("Creating test projects...")
        for data in PROJECTS:
            owner = created_users[data["owner_email"]]
            if Project.objects.filter(name=data["name"], owner=owner).exists():
                self.stdout.write(f"  Project '{data['name']}' already exists, skipping.")
                continue
            project = Project.objects.create(
                name=data["name"],
                description=data["description"],
                owner=owner,
                status=data.get("status", "open"),
                github_url=data.get("github_url", ""),
            )
            project.participants.add(owner)
            self.stdout.write(f"  Created project: {data['name']}")

        # Add some cross-participation and favorites
        projects = list(Project.objects.all())
        if len(projects) >= 2:
            maria = created_users["maria@yandex.ru"]
            alex = created_users["alex@gmail.com"]
            anna = created_users["anna@mail.ru"]
            ivan = created_users["ivan@yandex.ru"]

            alex_project = Project.objects.filter(owner=alex).first()
            anna_project = Project.objects.filter(owner=anna).first()
            ivan_project = Project.objects.filter(owner=ivan).first()
            maria_project = Project.objects.filter(owner=maria).first()

            if alex_project:
                alex_project.participants.add(maria)
                maria.favorites.add(alex_project)
            if anna_project:
                anna_project.participants.add(alex)
            if ivan_project:
                ivan_project.participants.add(anna)
                anna.favorites.add(ivan_project)
            if maria_project:
                alex.favorites.add(maria_project)

        self.stdout.write(self.style.SUCCESS("Done! Test data seeded successfully."))

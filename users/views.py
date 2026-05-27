from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
                surname=form.cleaned_data["surname"],
                password=form.cleaned_data["password"],
            )
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("projects:list")
            else:
                form.add_error(None, "Неверный имейл или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("projects:list")


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user, current_user=user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=user.pk)
    else:
        form = EditProfileForm(instance=user, current_user=user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = ChangePasswordForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list(request):
    all_users = User.objects.filter(is_active=True).order_by("-id")

    active_filter = None
    if request.user.is_authenticated:
        active_filter = request.GET.get("filter")
        if active_filter == "owners-of-favorite-projects":
            favorite_projects = request.user.favorites.all()
            all_users = User.objects.filter(
                owned_projects__in=favorite_projects, is_active=True
            ).distinct().order_by("-id")
        elif active_filter == "owners-of-participating-projects":
            participated = request.user.participated_projects.all()
            all_users = User.objects.filter(
                owned_projects__in=participated, is_active=True
            ).distinct().order_by("-id")
        elif active_filter == "interested-in-my-projects":
            my_projects = request.user.owned_projects.all()
            all_users = User.objects.filter(
                favorites__in=my_projects, is_active=True
            ).distinct().order_by("-id")
        elif active_filter == "participants-of-my-projects":
            my_projects = request.user.owned_projects.all()
            all_users = User.objects.filter(
                participated_projects__in=my_projects, is_active=True
            ).distinct().order_by("-id")
        else:
            active_filter = None

    paginator = Paginator(all_users, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_prefix = f"filter={active_filter}&" if active_filter else ""

    return render(request, "users/participants.html", {
        "participants": page_obj,
        "page_obj": page_obj,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    })

from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.services import get_page
from projects.forms import ProjectForm
from projects.models import Project


def project_list(request):
    projects = (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    page_obj = get_page(projects, request.GET.get("page"))
    return render(request, "projects/project_list.html", {
        "projects": page_obj,
        "page_obj": page_obj,
        "query_prefix": "",
    })


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if already_favorited := user.favorites.filter(pk=project_id).exists():
        user.favorites.remove(project)
    else:
        user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not already_favorited})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status == Project.STATUS_OPEN:
        project.status = Project.STATUS_CLOSED
        project.save()
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if user == project.owner:
        return JsonResponse(
            {"status": "error", "message": "Owner cannot toggle participation"},
            status=HTTPStatus.BAD_REQUEST,
        )
    if already_participating := project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
    else:
        project.participants.add(user)
    return JsonResponse({
        "status": "ok",
        "participant": not already_participating,
        "participating": not already_participating,
    })


@login_required
def favorite_projects(request):
    projects = (
        request.user.favorites
        .select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})

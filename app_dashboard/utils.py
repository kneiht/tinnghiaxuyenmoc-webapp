


from django.contrib.auth.models import User
from .models import Project, ProjectUser

def is_admin(user):
    # check if there is no user => allow to upload db
    if User.objects.count() == 0:
        return True
    else:
        return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser

def is_project_user(request, project_id):
    project = Project.objects.filter(pk=project_id).first()
    project_user = ProjectUser.objects.filter(project=project, user=request.user).first()
    if project_user:
        return True
    else:
        return False
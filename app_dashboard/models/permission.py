"""
This module defines permission-related models and functionality for the dashboard app.
Includes User permission management, role definitions, and dynamic permission creation.
"""

from django.utils import timezone
from django.contrib.auth.models import User
from django.apps import apps
from app_dashboard.models.base import models, BaseModel


def get_str_return(self):
    """
    Returns a string representation of the user, including the username
    and the first name. If the first name is not available, a default
    message is used instead.
    """
    if self.first_name in ("", None):
        name = "Chưa cập nhật tên"
    else:
        name = self.first_name
    return self.username + " (" + name + ")"


@classmethod
def get_display_fields(self):
    """
    Returns a list of fields for the User model that should be displayed in
    the admin interface. The list will only include fields that are actually
    available in the User model.
    """
    fields = [
        "username",
        "first_name",
        "email",
        "department",
        "position",
        "is_superuser",
    ]
    # Create a new list with only valid fields
    return [field for field in fields if hasattr(self, field)]


def check_permission(self, model):
    # Create a class to return
    class ReturnPermission:  # pylint: disable=R0903, W0621
        read = False
        create = False
        update = False
        delete = False
        approve = False
        lock = False

    # Create a new instance of the ReturnPermission class
    return_permission = ReturnPermission()

    # Check if the user is a superuser, grant all permissions
    if self.is_superuser:
        return_permission.read = True
        return_permission.create = True
        return_permission.update = True
        return_permission.delete = True
        return_permission.approve = True
        return_permission.lock = True
        return return_permission

    # Check if the  model is allowed to be displayed
    try:
        model_class = apps.get_model("app_dashboard", model)
    except LookupError:
        return return_permission

    if not hasattr(model_class, "allow_display"):
        return return_permission

    # Check if the model is allowed to be displayed
    if not model_class.allow_display:
        return return_permission

    # Get permission of a user
    try:
        user_permission = Permission.objects.filter(user=self).first()
    except AttributeError:
        # Handle case where objects manager is not available
        return return_permission

    # Check if the user has permission
    if not user_permission:
        return return_permission

    # Get permission of a model
    model = model.lower()
    if not hasattr(user_permission, model):
        return return_permission

    # Get permission of a model
    model_permission = getattr(user_permission, model)

    # Check if the user has permission
    for item in ["read", "create", "update", "delete", "approve", "lock"]:
        if item in model_permission:
            setattr(return_permission, item, True)

    return return_permission


@classmethod
def get_vietnamese_name(cls):
    if hasattr(cls, "vietnamese_name"):
        return cls.vietnamese_name
    else:
        return cls.__name__


User.add_to_class("__str__", get_str_return)
User.add_to_class("vietnamese_name", "Quản lý tài khoản")
User.add_to_class("get_display_fields", get_display_fields)
User.add_to_class("check_permission", check_permission)
User.add_to_class("get_vietnamese_name", get_vietnamese_name)

# Add department and position fields
User.add_to_class(
    "department",
    models.CharField(max_length=255, verbose_name="Bộ phận", default="", blank=True),
)
User.add_to_class(
    "position",
    models.CharField(max_length=255, verbose_name="Chức vụ", default="", blank=True),
)
User.add_to_class(
    "lock",
    models.BooleanField(
        verbose_name="Khóa sửa chữa",
        default=False,
    )
)
# Add verbose names for existing fields
User._meta.get_field("username").verbose_name = "Tên đăng nhập"
User._meta.get_field("first_name").verbose_name = "Tên người dùng"
User._meta.get_field("email").verbose_name = "Email"
User._meta.get_field("is_superuser").verbose_name = "Quyền admin"


class UserExtra(BaseModel):
    ROLE_CHOICES = (
        ("admin", "Quản Lý Cao Cấp"),
        ("technician", "Kỹ Thuật"),
        ("supervisor", "Giám Sát"),
        ("normal_staff", "Nhân Viên"),
        ("accountant", "Kế toán"),
    )
    role = models.CharField(
        max_length=255, choices=ROLE_CHOICES, default="normal_staff"
    )
    user: "User" = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to="images/avatars/", blank=True, null=True)
    settings = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username  # pylint: disable=E1101


def create_dynamic_permission_model(model_name="Permission"):
    MODEL_PERMISSION_CHOICES = (  # pylint: disable=C0103
        ("none", "Không"),
        ("read", "Đọc"),
        ("read_create", "Đọc/Tạo"),
        ("read_create_update", "Đọc/Tạo/Sửa"),
        ("read_create_update_delete", "Đọc/Tạo/Sửa/Xóa"),
        ("read_create_update_delete_approve", "Đọc/Tạo/Sửa/Xóa/Duyệt"),
        ("read_create_update_delete_approve_lock", "Đọc/Tạo/Sửa/Xóa/Duyệt/Khóa"),
    )
    attrs = {
        "vietnamese_name": "Cấp quyền sử dụng dữ liệu",
        "__module__": __name__,  # Set the module for the model
        "id": models.AutoField(primary_key=True),  # Add a default primary key
        "user": models.OneToOneField(
            User, on_delete=models.CASCADE, verbose_name="Tài khoản"
        ),
        "note": models.TextField(
            verbose_name="Ghi chú", default="", null=True, blank=True
        ),
        "created_at": models.DateTimeField(default=timezone.now),
        "Meta": type("Meta", (), {"ordering": ["user", "created_at"]}),
    }

    # Get all models from your app
    app_models = apps.get_app_config("app_dashboard").get_models()

    # Register any model that hasn't been registered yet with the default admin class
    for app_model in app_models:
        if not hasattr(app_model, "allow_display"):
            continue
        if not app_model.allow_display:
            continue
        # Get model name
        field_name = app_model.__name__.lower()

        if hasattr(app_model, "vietnamese_name"):
            verbose_name = app_model.vietnamese_name
        else:
            verbose_name = app_model.__name__

        attrs[field_name] = models.CharField(
            max_length=255,
            choices=MODEL_PERMISSION_CHOICES,
            default="none",
            verbose_name=verbose_name,
            null=True,
            blank=True,
        )

    # Add get_display_fields method
    @classmethod
    def get_display_fields(cls):
        fields = ["user", "note"]
        non_display_fields = ["archived", "last_saved", "created_at", "id"]
        # Add all dynamically created permission fields
        for field in cls._meta.get_fields():
            if field.name not in fields and field.name not in non_display_fields:
                fields.append(field.name)
        return fields

    attrs["get_display_fields"] = get_display_fields

    # Create the model dynamically
    return type(model_name, (BaseModel,), attrs)


# Create Permission
Permission = create_dynamic_permission_model()

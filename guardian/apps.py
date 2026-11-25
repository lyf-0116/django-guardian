from django.apps import AppConfig
from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.db.models.signals import m2m_changed, post_delete, post_migrate, post_save

from . import monkey_patch_group, monkey_patch_user


def _connect_permission_cache_invalidation() -> None:
    from .models import BaseObjectPermission
    from .signals import invalidate_obj_perms_cache

    for model in django_apps.get_models():
        if not issubclass(model, BaseObjectPermission):
            continue
        dispatch_uid = f"guardian.invalidate_obj_perms_cache.{model._meta.label_lower}"
        post_save.connect(invalidate_obj_perms_cache, sender=model, dispatch_uid=f"{dispatch_uid}.post_save")
        post_delete.connect(invalidate_obj_perms_cache, sender=model, dispatch_uid=f"{dispatch_uid}.post_delete")

    try:
        user_groups_through = get_user_model()._meta.get_field("groups").remote_field.through
    except (FieldDoesNotExist, AttributeError):
        return

    m2m_changed.connect(
        invalidate_obj_perms_cache,
        sender=user_groups_through,
        dispatch_uid="guardian.invalidate_obj_perms_cache.user_groups",
    )


class GuardianConfig(AppConfig):
    name = "guardian"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from .shortcuts import clear_ct_cache

        _connect_permission_cache_invalidation()
        post_migrate.connect(clear_ct_cache)
        if settings.GUARDIAN_MONKEY_PATCH_GROUP:
            monkey_patch_group()
        if settings.GUARDIAN_MONKEY_PATCH_USER:
            monkey_patch_user()

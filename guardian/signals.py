from guardian.core import ObjectPermissionChecker


def invalidate_obj_perms_cache(sender, instance, **kwargs) -> None:
    """Invalidate object permission snapshots after a permission row changes."""
    ObjectPermissionChecker.invalidate_cache()

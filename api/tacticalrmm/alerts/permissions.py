from django.shortcuts import get_object_or_404
from rest_framework import permissions

from tacticalrmm.permissions import _has_perm, _has_perm_on_agent


def _has_perm_on_alert(user, id: int):
    from alerts.models import Alert

    role = user.role
    if user.is_superuser or (role and getattr(role, "is_superuser")):
        return True

    # make sure non-superusers with empty roles aren't permitted
    elif not role:
        return False

    alert = get_object_or_404(Alert, id=id)

    if alert.agent:
        agent = alert.agent
    elif alert.assigned_check:
        agent = alert.assigned_check.agent
    elif alert.assigned_task:
        agent = alert.assigned_task.agent
    else:
        return True

    return _has_perm_on_agent(user, agent)


class AlertPerms(permissions.BasePermission):
    def has_permission(self, r, view):
        if r.method == "GET" or r.method == "PATCH":
            if "pk" in view.kwargs.keys():
                return _has_perm(r, "can_list_alerts") and _has_perm_on_alert(r.user, view.kwargs["pk"])
            else:
                return _has_perm(r, "can_list_alerts")
        else:
            if "pk" in view.kwargs.keys():
                return _has_perm(r, "can_manage_alerts") and _has_perm_on_alert(r.user, view.kwargs["pk"])
            else:
                return _has_perm(r, "can_manage_alerts")

class AlertTemplatePerms(permissions.BasePermission):
    def has_permission(self, r, view):
        if r.method == "GET":
            return _has_perm(r, "can_list_alerttemplates")
        else:
            return _has_perm(r, "can_manage_alerttemplates")
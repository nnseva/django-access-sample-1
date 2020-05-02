from django.db import models
from django.db.models import Q, F

from access.managers import AccessManager
from access.plugins import AccessPluginBase, CheckAblePlugin, ApplyAblePlugin, CompoundPlugin

from django.contrib.auth.models import User

from trans.models import Project, ProjectMember, Vehicle, Driver, Order

AccessManager.register_plugins({
    User: CompoundPlugin(
        CheckAblePlugin(
            appendable=(lambda model, request: 
                {} if request.user.id and request.user.projects.filter(allow_manage=True) else
                False
            ),
        ),
        ApplyAblePlugin(
            visible=(
                lambda queryset, request:
                    queryset if request.user.projects.filter(
                        allow_manage=True
                    ) else queryset.filter(
                        projects__project__users__user=request.user.id
                    ).distinct() or queryset.filter(
                        id=request.user.id
                    ).distinct()
            ),
            changeable=(lambda queryset, request: queryset.filter(id=request.user.id).distinct()),
            deleteable=(lambda queryset, request: queryset.filter(id=request.user.id).distinct())
        )
    ),
})

AccessManager.register_plugins({
    Project: CompoundPlugin(
        CheckAblePlugin(
            appendable=(lambda model, request: False),
        ),
        ApplyAblePlugin(
            visible=(lambda queryset, request: queryset.filter(
                users__user=request.user.id
            ).distinct()),
            changeable=(lambda queryset, request: queryset.filter(
                users__user=request.user.id,
                users__allow_manage=True
            ).distinct()),
            deleteable=(lambda queryset, request: queryset.none()),
        )
    ),
    ProjectMember: CompoundPlugin(
        CheckAblePlugin(
            appendable=(lambda model, request: {} if request.user.id and request.user.projects.filter(allow_manage=True) else False),
        ),
        ApplyAblePlugin(
            visible=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id
            ).distinct()),
            changeable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_manage=True
            ).distinct()),
            deleteable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_manage=True
            ).distinct()),
        )
    ),
})

AccessManager.register_plugins({
    Vehicle: CompoundPlugin(
        ApplyAblePlugin(
            visible=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id
            ).distinct()),
            changeable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_change=True
            ).distinct()),
            deleteable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_change=True
            ).distinct()),
        )
    ),
    Driver: CompoundPlugin(
        ApplyAblePlugin(
            visible=(lambda queryset, request: queryset.filter(
                Q(project__users__user=request.user.id) | Q(user=request.user)
            ).distinct()),
            changeable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_change=True
            ).distinct()),
            deleteable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_change=True
            ).distinct()),
        )
    ),
    Order: CompoundPlugin(
        ApplyAblePlugin(
            visible=(lambda queryset, request: queryset.filter(
                Q(
                    project__users__user=request.user.id
                ) | Q(
                    client=request.user
                ) | Q(
                    driver__user=request.user
                )
            ).distinct()),
            changeable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_change=True
            ).distinct()),
            deleteable=(lambda queryset, request: queryset.filter(
                project__users__user=request.user.id,
                project__users__allow_change=True
            ).distinct()),
        )
    ),
})

class SuperOnly(AccessPluginBase):
    def check_visible(self, model, request):
        return request.user.is_superuser and {}
    def check_changeable(self, model, request):
        return request.user.is_superuser and {}
    def check_appendable(self, model, request):
        return request.user.is_superuser and {}
    def check_deleteable(self, model, request):
        return request.user.is_superuser and {}

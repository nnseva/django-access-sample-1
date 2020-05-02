from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from access.admin import AccessModelAdmin, AccessControlMixin
from access.managers import AccessManager

from trans.models import Project, ProjectMember, Vehicle, Driver, Order
from django.contrib.auth.models import User, Group

from django.contrib.auth.admin import UserAdmin

admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class AccessUserAdmin(AccessControlMixin, UserAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(AccessUserAdmin, self).get_readonly_fields(request, obj) or []
        if request.user.is_superuser:
            return readonly_fields
        if not obj:
            return readonly_fields
        restrict = ['is_superuser', 'last_login', 'date_joined']
        if obj.pk != request.user.pk:
            restrict = ['is_superuser', 'last_login', 'date_joined', 'password', 'email']
        return [f for f in readonly_fields if f not in restrict] + restrict

    def get_list_display(self, request):
        fields = super(AccessUserAdmin, self).get_list_display(request) or []
        if request.user.is_superuser:
            return fields
        restrict = ['password', 'email']
        return [f for f in fields if not f in restrict]

    def _fieldsets_exclude(self, fieldsets, exclude):
        ret = []
        for nm, params in fieldsets:
            if 'fields' not in params:
                ret.append((nm, params))
                continue
            fields = []
            for f in params['fields']:
                if f not in exclude:
                    fields.append(f)
            pars = {}
            pars.update(params)
            pars['fields'] = fields
            ret.append((nm, pars))
        return ret

    def _fieldsets_only(self, fieldsets, only):
        ret = []
        for nm, params in fieldsets:
            if 'fields' not in params:
                ret.append((nm, params))
                continue
            fields = []
            for f in params['fields']:
                if f in only:
                    fields.append(f)
            pars = {}
            pars.update(params)
            pars['fields'] = fields
            ret.append((nm, pars))
        return ret

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super(AccessUserAdmin, self).get_fieldsets(request, obj)) or []
        fields = self.get_fields(request, obj=obj)
        return self._fieldsets_only(fieldsets, fields)

    def get_fields(self, request, obj=None):
        fields = list(super(AccessUserAdmin, self).get_fields(request, obj)) or []
        exclude = ['is_staff', 'groups', 'user_permissions']
        if not request.user.is_superuser:
            exclude = ['is_staff', 'is_superuser', 'groups', 'user_permissions']
            if obj and obj.pk != request.user.pk:
                exclude = ['is_staff', 'password', 'email', 'groups', 'user_permissions']
        return [f for f in fields if not f in exclude]

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        return super(AccessUserAdmin, self).save_model(request, obj, form, change)


@admin.register(Project)
class ProjectAdmin(AccessModelAdmin):
    fields = ['name']
    list_display = ['name']
    search_fields = ['name']

@admin.register(ProjectMember)
class ProjectMemberAdmin(AccessModelAdmin):
    fields = ['user', 'project', 'allow_manage', 'allow_change']
    list_display = ['user', 'project', 'allow_manage', 'allow_change']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'project__name']
    list_filters = ['project', 'allow_manage', 'allow_change']
    autocomplete_fields = ['user', 'project']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            projects = AccessManager(Project).changeable(request)
            kwargs["queryset"] = projects
        return super(ProjectMemberAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Vehicle)
class VehicleAdmin(AccessModelAdmin):
    fields = ['project', 'code']
    list_display = ['code', 'project']
    list_filters = ['project']
    search_fields = ['code']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            projects = Project.objects.filter(users__user=request.user, users__allow_change=True)
            kwargs["queryset"] = projects
        return super(VehicleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Driver)
class DriverAdmin(AccessModelAdmin):
    fields = ['project', 'user']
    list_display = ['user', 'project']
    list_filters = ['project']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'project__name']
    autocomplete_fields = ['user', 'project']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            projects = Project.objects.filter(users__user=request.user, users__allow_change=True)
            kwargs["queryset"] = projects
        return super(DriverAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Order)
class OrderAdmin(AccessModelAdmin):
    fields = ['project', 'client', 'vehicle', 'driver', 'start_time', 'stop_time']
    list_display = ['start_time', 'stop_time', 'client', 'driver', 'vehicle', 'project']
    list_filters = ['project', 'vehicle', 'driver']
    search_fields = ['client__username', 'client__first_name', 'client__last_name', 'project__name',]
    autocomplete_fields = ['client', 'vehicle', 'driver', 'project']
    date_hierarchy = 'start_time'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            projects = Project.objects.filter(users__user=request.user, users__allow_change=True)
            kwargs["queryset"] = projects
        return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Project(models.Model):
    name = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name=_('Name'),
        help_text=_('Name of the project')
    )
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

class ProjectMember(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=_('User'), help_text=_('User who belongs to this project'),
        related_name='projects',
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        verbose_name=_('Project'), help_text=_('Project to which this user belongs'),
        related_name='users',
    )
    allow_change = models.BooleanField(
        default=True,
        verbose_name=_('Allow Change'),
        help_text=_('Is the member allowed to change the project data?')
    )
    allow_manage = models.BooleanField(
        default=False,
        verbose_name=_('Allow Manage'),
        help_text=_('Is the member allowed to manage users for the project?')
    )

    def __str__(self):
        return _('%s -> %s') % (self.user, self.project)

    class Meta:
        verbose_name = _('Project Member')
        verbose_name_plural = _('Project Members')
        unique_together = (
            ('user', 'project'),
        )

class Vehicle(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        verbose_name=_('Project'), help_text=_('Project to which this vehicle belongs'),
        related_name='vehicles',
    )
    code = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name=_('Code'),
        help_text=_('Registration code')
    )
    def __str__(self):
        return self.code
    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
        unique_together = (
            ('code', 'project'),
        )

class Driver(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        verbose_name=_('Project'), help_text=_('Project to which this driver belongs'),
        related_name='drivers',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=_('User'), help_text=_('User who is a driver'),
        related_name='driving',
    )
    def __str__(self):
        return _('%s [%s]') % (self.user, self.project)

    class Meta:
        verbose_name = _('Driver')
        verbose_name_plural = _('Drivers')
        unique_together = (
            ('user', 'project'),
        )

class Order(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        verbose_name=_('Project'), help_text=_('Project to which this order belongs'),
        related_name='orders',
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=_('Client'), help_text=_('Client getting an order'),
        related_name='orders',
    )
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE,
        verbose_name=_('Vehicle'), help_text=_('Vehicle assigned to this order'),
        related_name='orders',
    )
    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE,
        verbose_name=_('Driver'), help_text=_('Driver assigned to this order'),
        related_name='orders',
    )
    start_time = models.DateTimeField(
        db_index=True,
        verbose_name=_("Start Time"),
        help_text=_("Time when the order is started")
    )
    stop_time = models.DateTimeField(
        db_index=True,
        verbose_name=_("Stop Time"),
        help_text=_("Time when the order is stopped")
    )
    def __str__(self):
        return _('%(start_time)s-%(stop_time)s %(client)s %(driver)s %(vehicle)s') % {
            'start_time': self.start_time,
            'stop_time': self.stop_time,
            'client': self.client,
            'driver': self.driver,
            'vehicle': self.vehicle,
        }
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

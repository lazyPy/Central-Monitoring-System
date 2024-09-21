# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class Vehicle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"


class MaintenanceSchedule(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    oil_change_start = models.DateField()
    oil_change_months = models.PositiveIntegerField()

    tire_change_start = models.DateField()
    tire_change_months = models.PositiveIntegerField()

    or_cr_renewal_start = models.DateField()
    or_cr_renewal_months = models.PositiveIntegerField()

    sprocket_change_start = models.DateField()
    sprocket_change_months = models.PositiveIntegerField()

    def is_maintenance_due(self, start_date, months):
        due_date = start_date + timedelta(days=30 * months)
        return date.today() >= due_date - timedelta(days=30)  # 30 days before due date

    def get_due_maintenances(self):
        due_maintenances = []
        if self.is_maintenance_due(self.oil_change_start, self.oil_change_months):
            due_maintenances.append("Oil change")
        if self.is_maintenance_due(self.tire_change_start, self.tire_change_months):
            due_maintenances.append("Tire change")
        if self.is_maintenance_due(self.or_cr_renewal_start, self.or_cr_renewal_months):
            due_maintenances.append("OR/CR renewal")
        if self.is_maintenance_due(self.sprocket_change_start, self.sprocket_change_months):
            due_maintenances.append("Sprocket change")
        return due_maintenances

    def __str__(self):
        return f"Maintenance Schedule for {self.vehicle}"

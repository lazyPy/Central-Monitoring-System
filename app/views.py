from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vehicle, MaintenanceSchedule
from datetime import date, timedelta


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Registration successful. Please login!')
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')

        if new_username != user.username and User.objects.filter(username=new_username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('edit_profile')

        if new_email != user.email and User.objects.filter(email=new_email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('edit_profile')

        user.username = new_username
        user.email = new_email

        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
            messages.success(request, 'Password updated successfully.')

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard')

    return render(request, 'edit_profile.html')


@login_required
def dashboard(request):
    vehicles = Vehicle.objects.filter(owner=request.user)

    upcoming_maintenance = []

    for vehicle in vehicles:
        try:
            schedule = vehicle.maintenanceschedule_set.get()
            due_maintenances = schedule.get_due_maintenances()
            if due_maintenances:
                upcoming_maintenance.append(f"{vehicle}: {', '.join(due_maintenances)}")
        except MaintenanceSchedule.DoesNotExist:
            pass

    context = {
        'vehicles': vehicles,
        'reminders': upcoming_maintenance,
    }

    return render(request, 'dashboard.html', context)


@login_required
def get_maintenance_schedule(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    schedule, created = MaintenanceSchedule.objects.get_or_create(vehicle=vehicle)

    if created:
        messages.info(request, f'New maintenance schedule created for {vehicle}.')

    data = {
        'oil_change_start': schedule.oil_change_start.isoformat() if schedule.oil_change_start else '',
        'oil_change_months': schedule.oil_change_months,
        'tire_change_start': schedule.tire_change_start.isoformat() if schedule.tire_change_start else '',
        'tire_change_months': schedule.tire_change_months,
        'or_cr_renewal_start': schedule.or_cr_renewal_start.isoformat() if schedule.or_cr_renewal_start else '',
        'or_cr_renewal_months': schedule.or_cr_renewal_months,
        'sprocket_change_start': schedule.sprocket_change_start.isoformat() if schedule.sprocket_change_start else '',
        'sprocket_change_months': schedule.sprocket_change_months,
    }

    return JsonResponse(data)


@login_required
def add_edit_vehicle(request, vehicle_id=None):
    if vehicle_id:
        vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    else:
        vehicle = None

    if request.method == 'POST':
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')

        if vehicle:
            vehicle.make = make
            vehicle.model = model
            vehicle.year = year
            vehicle.save()
            messages.success(request, f'Vehicle {vehicle} updated successfully.')
        else:
            new_vehicle = Vehicle.objects.create(owner=request.user, make=make, model=model, year=year)
            messages.success(request, f'New vehicle {new_vehicle} added successfully.')

        return redirect('dashboard')

    if vehicle:
        return JsonResponse({
            'id': vehicle.id,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year
        })

    return JsonResponse({})


@login_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    if request.method == 'POST':
        vehicle_name = str(vehicle)
        vehicle.delete()
        messages.success(request, f'Vehicle {vehicle_name} deleted successfully.')
    return redirect('dashboard')


@login_required
def add_maintenance_schedule(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    if request.method == 'POST':
        MaintenanceSchedule.objects.update_or_create(
            vehicle=vehicle,
            defaults={
                'oil_change_start': request.POST.get('oil_change_start'),
                'oil_change_months': request.POST.get('oil_change_months'),
                'tire_change_start': request.POST.get('tire_change_start'),
                'tire_change_months': request.POST.get('tire_change_months'),
                'or_cr_renewal_start': request.POST.get('or_cr_renewal_start'),
                'or_cr_renewal_months': request.POST.get('or_cr_renewal_months'),
                'sprocket_change_start': request.POST.get('sprocket_change_start'),
                'sprocket_change_months': request.POST.get('sprocket_change_months'),
            }
        )
        messages.success(request, f'Maintenance schedule for {vehicle} updated successfully.')

    return redirect('dashboard')

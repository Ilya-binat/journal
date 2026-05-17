from functools import wraps
from django.http import JsonResponse
from django.shortcuts import render, redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:401')

            if request.user.role not in roles:
                return redirect('users:403')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
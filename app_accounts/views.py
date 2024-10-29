# Python Standard Library Imports
from datetime import datetime
from decimal import Decimal

# Django and Other Third-Party Import
from django.contrib.auth import logout
from django.contrib.auth.views import (
    LoginView
)

from django.shortcuts import redirect, render
from django.urls import reverse

# App-Specific Imports
from .forms import (
    LoginForm, RegistrationForm
)

from django_ratelimit.decorators import ratelimit

from django.http import HttpResponse, HttpResponseForbidden

# AUTHENTICATION =============================================================
def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def register(request):
    return HttpResponse("Chỉ có admin mới có quyền tạo tài khoản")
    was_limited = getattr(request, 'limited', False)
    context = {'was_limited': was_limited}

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if was_limited:
            context['error_message'] = "Bạn đã tạo quá nhiều tài khoản trong một khoản thời gian ngắn. Vui lòng chờ 1 giờ sau để có thể tạo thêm tài khoản."
        else:
            if form.is_valid():            
                form.save()
                print('Tạo tài khoản thành công')
                context['account_message'] = "Bạn đã tạo tài khoản thành công! Đăng nhập ngay!"
            else:
                print("Tạo tài khoản thất bại!")
    else:
        form = RegistrationForm()
    context['form'] = form

    context['is_register'] = True
    context['title'] = "Tạo tài khoản"
    context['title'] = "Tạo tài khoản mới"
    context['button_name'] = "Tạo tài khoản mới"
    return render(request, 'pages/account.html', context)

def logout_view(request):
  logout(request)
  return redirect('login')

class UserLoginView(LoginView):
    template_name = 'pages/account.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_log_in'] = True
        context['title'] = "Đăng nhập vào hệ thống"
        context['button_name'] = "Đăng nhập"
        return context

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me:
            # Session will expire after 30 days
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
        else:
            # Session will expire when the user closes the browser
            self.request.session.set_expiry(0)
        return super().form_valid(form)

    def get_success_url(self):
        # Add your logic here to determine the dynamic redirect URL based on user conditions
        if is_admin(self.request.user):
            return reverse('page_home')  # Example: Redirect staff users to the admin interface
        else:
            return reverse('page_home')  # Example: Redirect other users to a dashboard













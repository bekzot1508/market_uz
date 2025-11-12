from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from user.forms import UserCreateForm, UserUpdateForm


# Create your views here.

################  REGISTER  ################
class RegisterView(View):
    def get(self, request):
        create_form = UserCreateForm()
        context = {
            'form': create_form,
        }
        return render(request,'user/register.html', context)

    def post(self, request):
        create_form = UserCreateForm(data=request.POST, files=request.FILES) # buni getdagisidan farqi userdan kelyotdan qiymatni dataga berib yuboramiz, data berish shart validatsiyaga  malumotlarimiz borishi va validatsiya bo'lishi uchun

        if create_form.is_valid():
            # create css account
            create_form.save()
            return redirect('user:login')

        else:
            context = {
                'form': create_form,
            }
            return render(request, 'user/register.html', context)

################  LOGIN  ################
class LoginView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        context = {
            'form': login_form,
        }
        return render(request,'user/login.html', context)

    def post(self, request):
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, 'You have been successfully logged in.')
            return redirect('home')
        else:
          return render(request, 'user/login.html', {"login_form": login_form})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been successfully logged out.')
        return redirect('home')


################  Profile  ################
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        # if not request.css.is_authenticated: ### LoginRequiredMixin ishlatganimiz uchun bu kod kerak emas
        #     return redirect('users:login')
        return render(request,'user/profile.html', {"user": request.user})



class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        user_update_form = UserUpdateForm(instance=request.user)
        return render(request,'user/profile_edit.html', {'form': user_update_form})

    def post(self, request):
        user_update_form = UserUpdateForm(instance=request.user, data=request.POST, files=request.FILES) # bu 2 ta parametr qabul qiladi, 1chi qaysi userni change qilyotganimiz, 2chisi qaysi malumot(data)larni change qilyotganimiz

        if user_update_form.is_valid():
            user_update_form.save()
            messages.success(request, 'You have been successfully updated your profile.')
            return redirect('user:profile')
        return render(request,'user/profile_edit.html', {'form': user_update_form})

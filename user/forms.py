from django import forms

from user.models import CustomUser


class UserCreateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture' ,'password') # ModelForm passwordni  sensitive data ekanligini bilmaydi, shuning uchun Save methodni override qilishimizkerak

    def save(self, commit=True):   # commit=True - bu modelFormni save methodini ovverida qilyotganda shunchaki yozib ketilishi shart bolgan elemant
        user = super().save(commit=False)   # parent ni super() methodini chaqiramiz, u bzga css yaratib beradi
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture', 'state', 'region', 'village', 'street', 'house')
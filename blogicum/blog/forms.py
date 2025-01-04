from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post, User


class ProfileFormMixin():
    class Meta:
        model = User
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email')


class ProfileForm(UserCreationForm):
    class Meta(ProfileFormMixin.Meta):
        fields: tuple = ProfileFormMixin.Meta.fields + ('password1',
                                                        'password2')


class EditProfileForm(forms.ModelForm):
    class Meta(ProfileFormMixin.Meta):
        pass


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

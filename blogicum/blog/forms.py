from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post, User
from .moderation import is_toxic
from core.constants import MODERATION_ERROR


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if is_toxic(text):
            raise ValidationError(MODERATION_ERROR)
        return text

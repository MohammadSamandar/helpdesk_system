from django import forms
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['title', 'description']
        labels = {
            'title':'عنوان تیکت',
            'description': 'شرح مشکل'
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs=
                                   {'rows':3, 'placeholder': 'پاسخ خود را اینجا بنویسید...'})
        }
        labels = {'body':''} # ما لیبل را خالی میگذاریم به دلیل داشتن placeholder
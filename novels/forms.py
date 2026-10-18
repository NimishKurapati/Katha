from django import forms
from .models import Novel, Chapter, WriterRequest


class NovelForm(forms.ModelForm):
    class Meta:
        model = Novel
        fields = ['title', 'cover_url', 'synopsis']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/cover.jpg'}),
            'synopsis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['chapter_number', 'title', 'content']
        widgets = {
            'chapter_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
        }


class WriterRequestForm(forms.ModelForm):
    class Meta:
        model = WriterRequest
        fields = ['reason']
        labels = {
            'reason': 'Why do you want to become a writer on LiteNovel Hub?'
        }
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share a brief pitch or synopsis of the light novel you plan to write...'
            }),
        }

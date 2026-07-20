from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'sticker', 'gif_url']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment or reply...',
            }),
            'gif_url': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text', '').strip()
        sticker = cleaned_data.get('sticker')
        gif_url = cleaned_data.get('gif_url', '').strip()
        if not text and not sticker and not gif_url:
            raise forms.ValidationError('Please add text, a sticker, or a GIF to submit your comment.')
        return cleaned_data

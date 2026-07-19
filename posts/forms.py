from django import forms
from .models import Post


class EditPostForm(forms.ModelForm):
    remove_image = forms.BooleanField(required=False, initial=False, label='Remove current photo')
    remove_video = forms.BooleanField(required=False, initial=False, label='Remove current video')

    class Meta:
        model = Post
        fields = ['content', 'image', 'video']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Update your confession text...',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('remove_image') and cleaned_data.get('image'):
            self.add_error('image', 'You cannot upload a new image and remove the current one at the same time.')
        if cleaned_data.get('remove_video') and cleaned_data.get('video'):
            self.add_error('video', 'You cannot upload a new video and remove the current one at the same time.')
        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)

        if self.cleaned_data.get('remove_image'):
            post.image = None
        if self.cleaned_data.get('remove_video'):
            post.video = None

        if commit:
            post.save()
        return post
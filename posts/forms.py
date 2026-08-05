import os

from django import forms

from .models import Post


def _is_allowed_image(filename):
    name = (filename or '').lower()
    return name.endswith(('.jpg', '.jpeg', '.png', '.webp'))


def _is_allowed_video(filename):
    name = (filename or '').lower()
    return name.endswith(('.mp4', '.webm', '.mov', '.m4v', '.ogg'))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts anonymously...',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        content = (cleaned_data.get('content') or '').strip()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')

        if not content and not image and not video:
            raise forms.ValidationError('Please add text or upload an image/video before posting.')

        if image is not None and not _is_allowed_image(getattr(image, 'name', '')):
            raise forms.ValidationError('Unsupported image type. Please upload JPG, PNG, or WEBP.')

        if video is not None and not _is_allowed_video(getattr(video, 'name', '')):
            raise forms.ValidationError('Unsupported video type. Please upload MP4, WEBM, MOV, M4V, or OGG.')

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and not _is_allowed_image(getattr(image, 'name', '')):
            raise forms.ValidationError('Unsupported image type. Please upload JPG, PNG, or WEBP.')
        return image

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and not _is_allowed_video(getattr(video, 'name', '')):
            raise forms.ValidationError('Unsupported video type. Please upload MP4, WEBM, MOV, M4V, or OGG.')
        return video


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
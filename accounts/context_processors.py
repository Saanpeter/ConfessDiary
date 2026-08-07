from .models import UserSettings


def user_settings(request):
    if request.user.is_authenticated:
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        return {'user_settings': settings_obj}
    return {}

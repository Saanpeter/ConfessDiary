from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoNewGoogleSignupAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        email = (sociallogin.user.email or '').strip()
        if not email:
            return False

        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(email__iexact=email).exists()

    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or '').strip()
        if not email:
            return

        from django.contrib.auth import get_user_model

        User = get_user_model()
        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user is not None:
            sociallogin.connect(request, existing_user)
            sociallogin.user = existing_user
        return super().pre_social_login(request, sociallogin)
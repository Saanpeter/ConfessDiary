from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoNewGoogleSignupAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.user.email

        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            return User.objects.filter(email=email).exists()

        return False
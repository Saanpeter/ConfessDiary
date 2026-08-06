from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoNewGoogleSignupAdapter(DefaultSocialAccountAdapter):
    """Legacy compatibility stub.

    Google sign-in is intentionally not restricted. This adapter remains as a no-op
    to avoid blocking any Google account from authenticating.
    """

    def is_auto_signup_allowed(self, request, sociallogin):
        return False

    def is_open_for_signup(self, request, *args, **kwargs):
        return False
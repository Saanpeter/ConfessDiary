from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoNewGoogleSignupAdapter(DefaultSocialAccountAdapter):
    """Legacy compatibility stub.

    Google sign-in is intentionally not restricted. This adapter remains as a no-op
    to avoid blocking any Google account from authenticating.
    """

    pass
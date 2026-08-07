from allauth.account.adapter import DefaultAccountAdapter


class NoSignupAccountAdapter(DefaultAccountAdapter):
    """Disable new form and social registration while preserving logins."""

    def is_open_for_signup(self, request):
        return False

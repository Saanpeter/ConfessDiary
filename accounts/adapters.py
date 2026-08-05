from allauth.account.adapter import DefaultAccountAdapter


class NoSignupAccountAdapter(DefaultAccountAdapter):
    """Legacy compatibility stub.

    This project intentionally uses Django Allauth's default signup behavior so
    existing users can sign in and Google OAuth works normally.
    """

    pass
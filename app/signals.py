from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    user.logged_in = True
    user.save()

@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    user.logged_in = False
    user.save()

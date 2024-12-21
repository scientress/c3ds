def make_superuser(response, user, backend, *args, **kwargs):
    user.is_superuser = True
    user.is_staff = True
    user.save()

from django.contrib.auth.models import User


def chairman_check(request):
    is_chairman = False
    if request.user.is_authenticated:
        is_chairman = User.objects.filter(username='chairman', pk=request.user.pk).exists()
    return {'is_chairman': is_chairman}

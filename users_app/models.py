from django.conf import settings
from helusers.models import AbstractUser


class CustomUser(AbstractUser):
    @property
    def is_ad_admin(self):
        # currently the Helsinki AD is not working
        # this is pending until Helsinki AD is fixed
        # TODO: change to check actual ad groups when Helsinki AD is fixed
        return settings.ALLOWED_ADMIN_AD_GROUPS is not None

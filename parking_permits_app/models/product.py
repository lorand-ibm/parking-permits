import json
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class Product(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    shared_product_id = models.UUIDField(
        unique=True, editable=False, blank=True, null=True
    )
    description = models.TextField(_("Description"), blank=True, null=True)
    name = models.CharField(_("Product name"), max_length=32, blank=False, null=False)

    def get_current_price(self):
        product_price = self.prices.get(
            start_date__lte=datetime.today(),
            end_date__gte=datetime.today(),
        )

        if product_price:
            return product_price.price
        else:
            return None

    class Meta:
        db_table = "product"
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name

    @property
    def namespace(self):
        return settings.NAMESPACE


def post_product_to_talpa(sender, instance, created, **kwargs):
    if created:
        data = {
            "namespace": settings.NAMESPACE,
            "namespaceEntityId": instance.pk,
            "name": instance.name,
        }
        result = requests.post(settings.TALPA_PRODUCT_EXPERIENCE_API, data=data)
        if result.status_code == 201:
            response = json.loads(result.text)
            instance.shared_product_id = response["productId"]
            instance.save()
        if result.status_code >= 300:
            raise Exception("Failed to create product on talpa: {}".format(result.text))


post_save.connect(post_product_to_talpa, sender=Product)

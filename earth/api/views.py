import random

from django.views.generic import TemplateView
from api.models import MarketingImage, EarthImage


class Homepage(TemplateView):
    template_name = 'earth/homepage.html'

    def get_context_data(self, **kwargs):
        image_ids = MarketingImage.objects\
            .prefetch_related('image')\
            .values_list('image_id', flat=True)
        return {
            'image': EarthImage.objects.get(id=random.choice(image_ids))
        }

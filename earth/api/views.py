import random

from django.views.generic import TemplateView
from api.models import EarthImage


class Homepage(TemplateView):
    template_name = 'earth/homepage.html'

    def get_context_data(self, **kwargs):
        image_ids = EarthImage.public\
            .filter(source='reddit')\
            .values_list('id', flat=True)
        return {
            'image': EarthImage.objects.get(id=random.choice(image_ids))
        }

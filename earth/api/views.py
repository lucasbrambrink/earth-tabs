import random

from django.views.generic import TemplateView
from api.models import EarthImage


class Homepage(TemplateView):
    template_name = 'earth/homepage.html'
    image_ids = []

    def get_image_ids(self):
        if not self.image_ids:
            self.image_ids = EarthImage.marketing\
                .values_list('id', flat=True)
        return self.image_ids

    def get_context_data(self, **kwargs):
        image_ids = self.get_image_ids()
        return {
            'image': EarthImage.objects.get(id=random.choice(image_ids))
        }

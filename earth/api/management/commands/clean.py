import logging
from django.core.management.base import BaseCommand
from api.models import EarthImage
from api.utils.image import InspectImage

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean all images for bad URLs'

    def handle(self, *args, **options):
        initial_count = EarthImage.objects.filter(is_public=False).count()
        for image in EarthImage.public.all():
            InspectImage.inspect(image, commit=True)

        final_count = EarthImage.objects.filter(is_public=False).count()

        logging.info('Invalidated {} urls'.format(final_count - initial_count))

import datetime
import logging
from django.core.management.base import BaseCommand
from api.models import EarthImage
from api.utils.image import InspectImage


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean all images for bad URLs'

    def add_arguments(self, parser):
        parser.add_argument('--only_resolution',
                            action='store_true',
                            dest='only_resolution',
                            default=False)
        parser.add_argument('--only_recents',
                            action='store_true',
                            dest='only_recents',
                            default=False)

    def handle(self, *args, **options):
        only_resolution = options.get('only_resolution')
        only_recents = options.get('only_recents')
        if only_resolution:
            queryset = EarthImage.public.filter(resolution_width__isnull=True)

            if only_recents:
                today = datetime.datetime.today()
                four_days_ago = today - datetime.timedelta(days=4)
                queryset = queryset.filter(create_date__gte=four_days_ago)

            logging.info('Starting with {} null resolutions'.format(queryset.count()))
            for image in queryset:
                InspectImage.inspect(image, commit=True)
            logging.info('Done!')
            return

        initial_count = EarthImage.objects.filter(is_public=False).count()
        for image in EarthImage.public.all():
            InspectImage.inspect(image, commit=True)

        final_count = EarthImage.objects.filter(is_public=False).count()

        logging.info('Invalidated {} urls'.format(final_count - initial_count))

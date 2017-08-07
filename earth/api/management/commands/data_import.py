import logging
from django.core.management.base import BaseCommand, CommandError
from api.data_sources.apod import ApodScraper
from api.data_sources.reddit import EarthScraper


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports 100 files from each registered data source'
    SIZE = 50

    def add_arguments(self, parser):
        parser.add_argument('--limit', nargs='+', dest='limit',
            type=int, default=self.SIZE)

    def handle(self, *args, **options):
        limit = options.get('limit')
        for scraper in (ApodScraper,
                        EarthScraper):
            scraper().batch_import(limit)

from PIL import Image
from io import BytesIO

from .scraping import ScrapingMixin


class InspectImage(ScrapingMixin,
                   object):

    @classmethod
    def as_buffer_obj(cls, data):
        return BytesIO(data)

    @classmethod
    def load_image(cls, url):
        response = cls.get_data(url, fail_silently=True)
        if response is None:
            raise ValueError('Unable to load image')

        return cls.as_buffer_obj(response)

    @classmethod
    def get_image(cls, url=None, image_data=None):
        if url is not None:
            image_data = cls.load_image(url)
        image = Image.open(image_data)
        return image

    @classmethod
    def inspect(cls, image_obj, commit=True):
        try:
            image = cls.get_image(url=image_obj.preferred_image_url)
        except (ValueError, OSError):
            image = None

        if image is not None:
            width, height = image.size
            image_obj.resolution_width = width
            image_obj.resolution_height = height
        else:
            image_obj.is_public = False
            image_obj.subreddit_name = 'Unable to load image'

        if commit:
            image_obj.save()

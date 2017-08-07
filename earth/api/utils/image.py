
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
        response = cls.get_data(url)
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
    def assign_resolution(cls, image_obj, commit=True):
        image = cls.get_image(url=image_obj.preferred_image_url)
        width, height = image.size
        image_obj.resolution_width = width
        image_obj.resolution_height = height
        if commit:
            image_obj.save()

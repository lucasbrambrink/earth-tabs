
var API_URL = 'https://earth-pics.tk/api/v0/earth';
// var API_URL = 'http://127.0.0.1:8000/api/v0/earth';


// Attempt to get a photo from local storage
var cachedImage = localStorage.getItem('cachedImage');
if (cachedImage !== null && cachedImage !== undefined && cachedImage !== 'undefined') {
    setImage(JSON.parse(cachedImage));
}

var settings = {};
loadOrCreateSettings(settings, true);

function setLastSeenImage(cachedImage) {
    var lastImage = localStorage.getItem('lastImage');
    var $links = $('a.last');
    if (lastImage === null) {
        $links.remove();
        $('nav span').remove();
    } else {
        var links = lastImage.split('|');
        $('a.last-link').attr('href', links[0]);
        $('a.last-image-link').attr('href', links[1]);
    }
    localStorage.setItem('lastImage',
        cachedImage.permalink + '|' + cachedImage.preferred_image_url);
}

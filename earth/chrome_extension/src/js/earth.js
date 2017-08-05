
var API_URL = 'https://earth-pics.tk/api/v0/earth';
var getNewSettings = function () {
    $.getJSON(API_URL + '/settings/new/')
        .success(function(resp) {
            chrome.storage.sync.set({"settings_uid": resp.url_identifier});
            settings['uid'] = resp.url_identifier;
            console.log('success!', resp);
        })
        .fail(function (resp) {
            console.log(resp);
        });
};

// Attempt to get a photo from local storage
var cachedImage = localStorage.getItem('cachedImage');
if (cachedImage !== null && cachedImage !== undefined && cachedImage !== 'undefined') {
    setImage(JSON.parse(cachedImage));
}

var settings = {};
chrome.storage.sync.get("settings_uid", function(item) {
    if (item === null || item === undefined) {
        getNewSettings();
    }
    getNewImage(item.settings_uid);
    settings['uid'] = item.settings_uid;
});

function setLastSeenImage(cachedImage) {
    var lastImage = localStorage.getItem('lastImage');
    var $link = $('.last-image');
    if (lastImage === null) {
        $link.remove();
        $('nav span').remove();
    } else {
        $link.attr('href', lastImage);
    }
    localStorage.setItem('lastImage', cachedImage.permalink);
}


function setImage(imageData) {
    $('.image').css("background-image", "url('" + imageData.preferred_image_url + "')");

    $('.title')
        .attr("href", imageData.permalink)
        .html(imageData.title);
    $('.author').html("-- " + imageData.author);
    $('.ups').html(imageData.ups);
    setLastSeenImage(imageData);
}


function getNewImage(settings_uid) {
    var url = API_URL + '/get';

    if (settings_uid !== null && settings_uid !== undefined) {
        url += '/' + settings_uid;
    } else {
        getNewSettings();
    }
    console.log(url);

    $.getJSON(url)
        .complete(function(resp) {
            var newImage = resp;
            console.log(resp);
            cachedImage = localStorage.getItem('cachedImage');
            localStorage.removeItem('cachedImage');
            localStorage.setItem('cachedImage', JSON.stringify(newImage));
            // console.log(resp);
            if (cachedImage === null) {
                setImage(newImage);
                getNewImage(settings_uid);
            }
            $('#cached-image').attr('src', newImage.preferred_image_url);
        }).fail(function () {
            console.log('Image Request Failed');
        });
}

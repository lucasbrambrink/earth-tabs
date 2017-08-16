/**
 * Created by lucasbrambrink on 8/5/17.
 */


function setImage(imageData) {
    $('.image').css("background-image", "url('" + imageData.preferred_image_url + "')");
    if (imageData.contain_image) {
        $('.image').css("background-size", "contain");
    }
    $('.title')
        .attr("href", imageData.permalink)
        .html(imageData.title);
    $('.author').html("-- " + imageData.author);
    $('.ups').html(imageData.ups);
    setLastSeenImage(imageData);
}

var getRandomToken = function () {
    var randomPool = new Uint8Array(32);
    crypto.getRandomValues(randomPool);
    var hex = '';
    for (var i = 0; i < randomPool.length; ++i) {
        hex += randomPool[i].toString(16);
    }
    return hex;
};

function getNewImage(settings_uid) {
    var url = API_URL + '/get';

    if (typeof settings_uid === 'string') {
        url += '/' + settings_uid;
    }

    $.getJSON(url)
        .success(function(resp) {
            var newImage = resp;
            cachedImage = localStorage.getItem('cachedImage');
            localStorage.removeItem('cachedImage');
            localStorage.setItem('cachedImage', JSON.stringify(newImage));
            if (cachedImage === null) {
                setImage(newImage);
                getNewImage(settings_uid);
            }
            $('#cached-image').attr('src', newImage.preferred_image_url);
        }).fail(function () {
            console.log('Image Request Failed');
        });
}

var loadOrCreateSettings = function (settings, load_image) {
    chrome.storage.sync.get(['token', 'settings_uid'], function(items) {
        var token = items.token;
        if (!token) {
            token = getRandomToken();
            chrome.storage.sync.set({token: token});
        }
        settings.token = token;

        var loadImageCallback = function(uid) {
            if (load_image) {
                getNewImage(uid);
            }
        };

        var uid = items.settings_uid;
        if (uid) {
            settings.uid = uid;
            loadImageCallback(settings.uid);
        }
        else {
            $.ajax({
                url: API_URL + '/settings/new',
                method: 'POST',
                headers: {'token': settings.token}
            }).success(function(resp) {
                chrome.storage.sync.set({"settings_uid": resp.url_identifier});
                settings.uid = resp.url_identifier;
                loadImageCallback(settings.uid);
            });
        }
    });
};


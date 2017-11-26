/**
 * Created by lucasbrambrink on 8/5/17.
 */


function setImage(imageData) {
    var image = $('.image');
    image.css("background-image", "url('" + imageData.preferred_image_url + "')");
    var background_size = imageData.contain_image ? "contain" : "cover";
    image.css("background-size", background_size);
    $('.title')
        .attr("href", imageData.permalink)
        .html(imageData.title);
    $('.author').html("-- " + imageData.author);
    $('.ups').html(imageData.ups);
    var admin = $('.administrator');
    if (imageData.is_administrator) {
        admin.on('click', function(event) {
            event.preventDefault();
            $.ajax({
                url: API_URL + '/get/' + settings.uid + '/' + imageData.id,
                method: 'DELETE',
                headers: {'token': settings.token}
            }).success(function(resp, textStatus, xhr) {
                console.log(resp);
                if (xhr.status === 202) {
                    admin.text('Inactivated');
                } else {
                    console.log(resp);
                }
            });
        });
    } else {
        admin.remove();
        $('nav span.administrator-span').remove();
    }
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
            } else {
                setLastSeenImage(newImage);
            }
            $('#cached-image').attr('src', newImage.preferred_image_url);
        }).fail(function () {
            console.log('Image Request Failed');
        });
}

function setLastSeenImage(cachedImage) {
    var lastImage = localStorage.getItem('lastImage');
    var $links = $('a.last');
    if (lastImage === null) {
        $links.remove();
        $('nav span.last-image-span').remove();
    } else {
        var links = lastImage.split('|');
        $('a.last-link').attr('href', links[0]);
        $('a.last-image-link').attr('href', links[1]);
    }
    localStorage.setItem('lastImage',
        cachedImage.permalink + '|' + cachedImage.preferred_image_url);
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
            if (window.vmSettings) {
                window.vmSettings.getSettings();
            }
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
                url: API_URL + '/settings/new/',
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


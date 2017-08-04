// Get Options

// chrome.topSites.get(top_sites);

// var random_sub = [];

// function restore_options() {
//
//     chrome.storage.sync.get({
//         show_title: true,
//         show_sites: false,
//         subreddits: true
//     }, function (items) {
//
//
//         if (items.show_title == false) {
//             $('.info').css('display', 'none');
//         }
//         if (items.show_sites == true) {
//             $('.top_sites').css('display', 'inherit');
//         }
//
//         subreddit = items.subreddits;
//         x = 0;
//         for (var index in subreddit) {
//
//             if (subreddit[index] == 1) {
//                 //    console.log(index);
//                 random_sub[x] = index;
//                 x++;
//             }
//
//         }
//
//         subreddit = random_sub[Math.floor(Math.random() * random_sub.length)];
//         if (subreddit == null) {
//             subreddit = 'earthporn';
//         }
//
//         new_photo(subreddit);
//
//     });
//
// }
var API_URL = 'https://earth-pics.tk/api/v0/earth/get';
var REDDIT_URL = 'https://reddit.com';
// var callback = function(items) {
//     settings_identifier = items.settings_uid;
// }


// Attempt to get a photo from local storage
var cachedImage  = localStorage.getItem('cachedImage');
if (cachedImage !== null) {
    setImage(JSON.parse(cachedImage));
}
var settings = {};
chrome.storage.sync.get("settings_uid", function(item) {
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
        $link.attr('href', REDDIT_URL + lastImage);
    }
    localStorage.setItem('lastImage', cachedImage.permalink);
}


function setImage(imageData) {
    $('.image').css("background-image", "url('" + imageData.preferred_image_url + "')");

    $('.title')
        .attr("href", REDDIT_URL + imageData.permalink)
        .html(imageData.title);
    $('.author').html("-- " + imageData.author);
    $('.ups').html(imageData.ups);
    setLastSeenImage(imageData);
}


function getNewImage(settings_uid) {
    var url = API_URL;

    if (settings_uid !== null) {
        url += '/' + settings_uid;
    }
    console.log(url);

    $.getJSON(url)
        .success(function(resp) {
            newImage = resp;
            localStorage.removeItem('cachedImage');
            localStorage.setItem('cachedImage', JSON.stringify(newImage));
            if (cachedImage === null) {
                setImage(newImage);
            } else {
                $('.cached-image')
                    .css("background-image", "url('" + imageData.preferred_image_url + "')");
            }
        }).fail(function () {
            console.log('Image Request Failed');
        });
}

// function top_sites(data) {
//
//     $.each(data, function (index, value) {
//
//         $('.top_sites').append("<div class='site_container'><div class='site'><a href='" + value.url + "'>" + value.title.substring(0, 25) + "..<div class='url'>" + value.url + "</div></div></a></div>");
//         index++;
//         if (index == 5)
//             return false;
//     });
//
// }


// document.addEventListener('DOMContentLoaded', restore_options);

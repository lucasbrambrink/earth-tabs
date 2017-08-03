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

// var callback = function(items) {
//     settings_identifier = items.settings_uid;
// }


// Attempt to get a photo from local storage
var currentImage = null; //localStorage.getItem('currentImage');
if (currentImage === null) {
    chrome.storage.sync.get("settings_uid", function (item) {
        getNewImage(item.settings_uid);
    });
} else {
    setImage(JSON.parse(currentImage));
}


function setImage(imageData) {
    $('.image').css("background-image", "url('" + imageData.preferred_image_url + "')");

    $('.title')
        .attr("href", "http://reddit.com" + imageData.permalink)
        .html(imageData.title);
    $('.author').html("By " + imageData.author);
    $('.ups').html(imageData.ups);

}

// // cache photo as previous
// var lastPhoto = localStorage.getItem('lastPhoto');
// if (lastPhoto === null) {
//     $('.last-title').remove();
// } else {
//     $('.last-title').attr('href', "http://reddit.com" + lastPhoto);
// }
// localStorage.setItem('lastPhoto', the_image.permalink);

function getNewImage(settings_uid) {
    var url = API_URL;

    if (settings_uid !== null) {
        url += '/' + settings_uid;
    }
    console.log(url);

    $.getJSON(url)
        .success(function(resp) {
            newImage = resp;
            localStorage.removeItem('currentImage');
            localStorage.setItem('currentImage', JSON.stringify(newImage));
            setImage(newImage);
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

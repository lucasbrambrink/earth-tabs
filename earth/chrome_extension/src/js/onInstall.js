function analytics(action) {
  var _gaq = _gaq || [],
    manifest = chrome.runtime.getManifest();

  _gaq.push(['_setAccount', 'UA-1376968-25']);
  _gaq.push(['_trackPageview', '/' + action]);




}


  (function() {
    var ga, s;

    ga = document.createElement('script');
    ga.type = 'text/javascript';
    ga.async = true;
    ga.src = 'https://ssl.google-analytics.com/ga.js';

    s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(ga, s);
  })();

  

/**
 * On uninstall extension.
 */
function onSuspend() {
  analytics('suspend');
}


function loadJSON(path, success, error)
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                if (success)
                    success(JSON.parse(xhr.responseText));
            } else {
                if (error)
                    error(xhr);
            }
        }
    };
    xhr.open("GET", path, true);
    xhr.send();
}

/**
 * Get the first random picture and store it in localStorage.
 * Caching the first call image.
 */
function onInit() {
// Cache first call here

loadJSON('http://labs.ryandury.com/r/earthporn',
         function(data) { 

var dataToStore = JSON.stringify(data);
  localStorage.removeItem('photo');
  localStorage.setItem('photo', dataToStore);

         }

);



  analytics('install');
}

/**
 * Add event listeners
 */
chrome.runtime.onInstalled.addListener(onInit);
chrome.runtime.onSuspend.addListener(onSuspend);
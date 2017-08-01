/****** Settings *****

1. without any settings specified, will operate on default values
2. if settings are visited, ask API to provide new UID
3. on save, POST to backend using UID to link to settings object
    - auth/security not *really* necessary but might be a nice-to-have
4. earth.js will fetch UID (from chrome.storage) and use to make API image request


*/
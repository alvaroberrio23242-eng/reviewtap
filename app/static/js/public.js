/* ReviewTap Public Profile — Event Tracking */
(function () {
  'use strict';

  function getDeviceCode() {
    var match = window.location.pathname.match(/\/r\/([A-Z0-9]{8})/);
    return match ? match[1] : '';
  }

  function trackClick(channel) {
    if (!navigator.sendBeacon) return;
    var dc = getDeviceCode();
    var url = '/track' + (dc ? '?dc=' + dc : '');
    var data = new FormData();
    data.append('channel', channel);
    navigator.sendBeacon(url, data);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var buttons = document.querySelectorAll('.channel-btn[data-channel]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', function () {
        trackClick(this.getAttribute('data-channel'));
      });
    }
  });
})();

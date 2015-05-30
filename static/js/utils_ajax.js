(function () {
"use strict";

var createXMLHttpRequest = null;

if (window.XMLHttpRequest) {
	createXMLHttpRequest = function() { return new XMLHttpRequest(); };
}
else {
	createXMLHttpRequest = function() { return new ActiveXObject("Microsoft.XMLHTTP"); };
}

var xhrSend = function(type, url, data, successFn, failFn) {
	var req = createXMLHttpRequest();
	req.open(type, url, true);
	req.setRequestHeader("X-CSRFToken", _utils.getCookie("csrftoken"));
	req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
	if (type == "POST") {
		req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	}
	req.setRequestHeader("Content-length", data.length);
	req.setRequestHeader("Connection", "close");

	req.onreadystatechange = function () {
		if (req.readyState != 4) return;
		if (req.status >= 200 && req.status < 400) {
			if (successFn != undefined) {
				var contentType = req.getResponseHeader('content-type');
				var data = req.responseText;
				if (contentType.indexOf('application/json') === 0) {
					data = JSON.parse(data);
				}
				successFn(data, req);
			}
		}
		else {
			if (successFn != undefined) {
				failFn(req);
			}
		}
	}
	req.send(data);
};

window._utils.xhrSend = xhrSend;

}());

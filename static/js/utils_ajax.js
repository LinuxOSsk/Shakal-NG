(function () {
"use strict";

var createXMLHttpRequest = null;

if (window.XMLHttpRequest) {
	createXMLHttpRequest = function() { return new XMLHttpRequest(); };
}
else {
	createXMLHttpRequest = function() { return new ActiveXObject("Microsoft.XMLHTTP"); };
}

var xhrSend = function(options) {
	var type = options.type || 'GET';
	var url = options.url;
	var data = options.data || '';
	var successFn = options.successFn;
	var failFn = options.failFn;
	var headersFn = options.headersFn;
	var req = createXMLHttpRequest();
	var extraHeaders = options.extraHeaders || {};
	req.open(type, url, true);
	req.setRequestHeader('X-CSRFToken', _utils.getCookie('csrftoken'));
	req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
	if (options.contentType !== undefined) {
		if (options.contentType !== null) {
			req.setRequestHeader('Content-type', options.contentType);
		}
	}
	else {
		if (type == 'POST') {
			req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
		}
	}
	for (var header in extraHeaders) {
		req.setRequestHeader(header, extraHeaders[header]);
	}

	req.onreadystatechange = function () {
		if (req.readyState === 2) {
			if (headersFn !== undefined) {
				headersFn(req);
			}
		}
		if (req.readyState != 4) return;

		var contentType = req.getResponseHeader('content-type');
		var data = req.responseText;
		if (contentType.indexOf('application/json') === 0) {
			data = JSON.parse(data);
		}

		if (req.status >= 200 && req.status < 400) {
			if (successFn != undefined) {
				successFn(data, req, options);
			}
		}
		else {
			if (failFn != undefined) {
				failFn(data, req, options);
			}
		}
	}
	req.send(data);
};

window._utils.xhrSend = xhrSend;

}());

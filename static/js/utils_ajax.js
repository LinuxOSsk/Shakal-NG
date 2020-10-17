(function(_) {

"use strict";

function ajaxForwardError(response) {
	if (response.status !== 0 && response.responseText) {
		document.open();
		document.write(response.responseText); // jshint ignore:line
		document.close();
		if (window.history !== undefined) {
			window.history.replaceState({}, null, window.location);
		}
	}
	else {
		if (window.console) {
			console.log("Response error, status: " + response.status);
		}
	}
}

_.ajaxForwardError = ajaxForwardError;


function xhrSend(options) {
	var opts = _.lightCopy(options);
	opts.method = options.method || 'GET';
	opts.crossOrigin = options.crossOrigin || false;
	var req = new XMLHttpRequest();
	var extraHeaders = options.extraHeaders || {};

	if (window._settings && window._settings.debug) {
		opts.failFn = opts.failFn || ajaxForwardError;
	}

	if (options.progress) {
		_.bindEvent(req.upload, 'progress', options.progress);
	}

	var data = opts.data;
	if (typeof data != 'string' && !(window.FormData !== undefined && data instanceof window.FormData)) {
		data = _.encodeURLParameters(data);
	}

	req.open(opts.method, opts.url, true);
	if (opts.method === 'GET' && opts.cache === false) {
		req.setRequestHeader('Cache-control', 'no-cache, must-revalidate, post-check=0, pre-check=0');
		req.setRequestHeader('Cache-control', 'max-age=0');
		req.setRequestHeader('Expires', '0');
		req.setRequestHeader('Expires', 'Tue, 01 Jan 1980 1:00:00 GMT');
		req.setRequestHeader('Pragma', 'no-cache');
	}

	if (!opts.crossOrigin) {
		if (!_.has(extraHeaders, 'X-CSRFToken')) {
			var tokenCookie = _.getCookie('csrftoken');
			if (tokenCookie !== null) {
				req.setRequestHeader('X-CSRFToken', tokenCookie);
			}
		}
		if (!_.has(extraHeaders, 'X-Requested-With')) {
			req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
		}
	}
	if (options.contentType !== undefined) {
		if (options.contentType !== null) {
			req.setRequestHeader('Content-type', options.contentType);
		}
	}
	else {
		if (opts.method == 'POST') {
			if (!(window.FormData !== undefined && data instanceof window.FormData)) {
				req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
			}
		}
	}

	for (var header in extraHeaders) {
		req.setRequestHeader(header, extraHeaders[header]);
	}

	req.onreadystatechange = function () {
		if (req.readyState === 2) {
			if (opts.headersFn !== undefined) {
				opts.headersFn(req);
			}
		}
		if (req.readyState != 4) return;
		if (req.status >= 200 && req.status < 400) {
			if (opts.successFn !== undefined) {
				var contentType = req.getResponseHeader('content-type');
				var data = req.responseText;
				if (contentType.indexOf('application/json') === 0) {
					data = JSON.parse(data);
					req.isJSON = true;
				}
				opts.successFn(data, req, options);
			}
		}
		else {
			if (opts.failFn !== undefined) {
				opts.failFn(req, options);
			}
		}
	};
	req.send(data);
}


_.xhrSend = xhrSend;
_.ajaxForwardError = ajaxForwardError;


}(_utils2));

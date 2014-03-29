// Cookies

(function (window, document) {
	"use strict";

	var setCookie = function(name, value, days, path) {
		var expires = "";
		if (days) {
			var date = new Date();
			date.setTime(date.getTime() + (days*24*60*60*1000));
			expires = "; expires=" + date.toGMTString();
		}
		if (path == undefined) {
			path = "; path=/"
		}
		document.cookie = name + "="+encodeURIComponent(value) + expires + path;
	};

	var getCookie = function(name) {
		var cookies = document.cookie.split(';');
		for(var i = 0; i < cookies.length; i++) {
			var cookieName = cookies[i].substr(0, cookies[i].indexOf('='));
			var value = cookies[i].substr(cookies[i].indexOf('=') + 1);
			cookieName = cookieName.replace(/^\s+|\s+$/g,"");
			if (cookieName == name) {
				return decodeURIComponent(value);
			}
		}
		return null;
	};

	var deleteCookie = function(name) {
		setCookie(name, "", -1);
		setCookie(name, "", -1, "");
	};

	window.cookiemanager = {setCookie: setCookie, getCookie: getCookie, deleteCookie: deleteCookie};

})(this, this.document);


// Load libraries
(function (window, document) {
	"use strict";

	var head = document.getElementsByTagName('head')[0];
	var loadedScripts = [];
	var registeredScripts = [];
	var waitingCallbacks = [];

	var scriptIsReady = function(state) {
		return (state === 'loaded' || state === 'complete' || state === 'uninitialized' || !state);
	}

	var fireCallbacks = function() {
		var firedCallbacks = [];
		for (var i = 0; i < waitingCallbacks.length; ++i) {
			var callback = waitingCallbacks[i][0];
			var paths = waitingCallbacks[i][1];
			var allLoaded = true;
			for (var j = 0; j < paths.length; ++j) {
				if (loadedScripts.indexOf(paths[j]) == -1) {
					allLoaded = false;
					break;
				}
			}
			if (allLoaded) {
				firedCallbacks.push(i);
				callback();
			}
		}
		firedCallbacks.reverse();
		for (var i = 0; i < firedCallbacks.length; ++i) {
			waitingCallbacks.splice(firedCallbacks[i], 1);
		}
	}

	var loader = function(paths, callback) {
		var missingPaths = [];
		for (var i = 0; i < paths.length; ++i) {
			if (registeredScripts.indexOf(paths[i]) == -1) {
				missingPaths.push(paths[i]);
				registeredScripts.push(paths[i]);
			}
		}

		waitingCallbacks.push([callback, paths]);

		for (var i = 0; i < missingPaths.length; ++i) {
			var path = missingPaths[i];
			var script = document.createElement('script');
			script.src = path;
			script.onreadystatechange = script.onload = function(path) {
				return function() {
					if (scriptIsReady(script.readyState)) {
						loadedScripts.push(path);
						fireCallbacks();
					}
				};
			}(path);
			head.appendChild(script);
		}

		setTimeout(fireCallbacks, 0);
	};

	var getLoader = function() { return loader };
	window.loader = getLoader();
})(this, this.document);

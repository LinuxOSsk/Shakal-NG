(function() {

"use strict";


function checkFeatures(features) {
	for (var i = 0; i < features.length; ++i) {
		switch (features[i]) {
			case "ajax":
				return window.XMLHttpRequest !== undefined;
			case "history_push":
				if (window.history && window.history.pushState) {
					return true;
				}
				else {
					return false;
				}
				break;
			case "touch":
				return "ontouchstart" in window;
			case "drop":
				return "ondrop" in window;
			case "file":
				return "File" in window && "FileReader" in window;
			default:
				return false;
		}
	}
	return true;
}


var body = document.body;
var ap = Array.prototype;

if (!Element.prototype.matches) {
	Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
}


function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function setCookie(name, value, days) {
	var expires;
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		expires = "; expires="+date.toGMTString();
	}
	else {
		expires = "";
	}
	document.cookie = name+"="+value+expires+"; path=/";
}

function has(obj, key) {
	return Object.prototype.hasOwnProperty.call(obj, key);
}

function lightCopy(obj) {
	var copy = {};
	for (var prop in obj) {
		if (has(obj, prop)) {
			copy[prop] = obj[prop];
		}
	}
	return copy;
}

function forEachDict(collection, fn) {
	for (var key in collection) {
		if (has(collection, key)) {
			var value = collection[key];
			fn(key, value);
		}
	}
}

function dictToPairs(collection) {
	var pairs = [];
	forEachDict(collection, function(key, value) {
		pairs.push([key, value]);
	});
	return pairs;
}

function pairsToDict(collection) {
	var dict = {};
	collection.forEach(function(item) {
		dict[item[0]] = item[1];
	});
	return dict;
}

function encodeURLParameters(parameters) {
	var urlParameterList = parameters;
	if (!Array.isArray(parameters)) {
		urlParameterList = dictToPairs(urlParameterList);
	}

	var urlComponents = [];
	urlParameterList.forEach(function(parameter) {
		urlComponents.push(encodeURIComponent(parameter[0]) + '=' + encodeURIComponent(parameter[1]));
	});
	return urlComponents.join('&');
}

var eventClasses = {
	click: MouseEvent
};

function triggerEvent(element, name, memo, bubbles) {
	var cls = eventClasses[name] || Event;
	var event = new cls(name, {bubbles: bubbles === false ? false : true});
	event.memo = memo || { };
	element.dispatchEvent(event);
}

function bindEvent(element, name, fn) {
	element.addEventListener(name, fn, false);
}

function unbindEvent(element, name, fn) {
	element.removeEventListener(name, fn, false);
}

function onLoad(callback) {
	if (document.body) {
		callback({memo: document.body});
		bindEvent(document.body, 'contentloaded', callback);
	}
	else {
		document.addEventListener("DOMContentLoaded", function(event) {
			callback({memo: document.body});
			bindEvent(document.body, 'contentloaded', callback);
		});
	}
}

function onUnload(callback) {
	bindEvent(document.body, 'contentunloaded', callback);
}

function triggerLoad(element) {
	triggerEvent(document.body, 'contentloaded', element, false);
}

function triggerUnload(element) {
	triggerEvent(document.body, 'contentunloaded', element, false);
}

function unbindOnLoad(callback) {
	if (document.body) {
		unbindEvent(document.body, 'contentloaded', callback);
	}
	else {
		document.addEventListener("DOMContentLoaded", function(event) {
			unbindEvent(document.body, 'contentloaded', callback);
		});
	}
}

function unbindOnUnLoad(callback) {
	unbindEvent(document.body, 'contentunloaded', callback);
}

function getAttachToElement(attachTo) {
	if (attachTo === undefined) {
		attachTo = document.body;
	}
	if (attachTo.binderListeners === undefined) {
		attachTo.binderListeners = {};
	}
	return attachTo;
}

function eventProcessor(eventType, binderListeners) {
	return function(e) {
		var target = e.target;
		var eventListeners = binderListeners[eventType];
		binderListeners[eventType].forEach(function(listener) {
			var selector = listener[0];
			var fn = listener[1];
			if (selector === null || target.matches(selector)) {
				fn(e, target);
			}
			else {
				var closest = target.closest(selector);
				if (closest !== null) {
					fn(e, closest);
				}
			}
		});
	};
}

function listen(selector, event, fn, attachTo) {
	attachTo = getAttachToElement(attachTo);
	var binderListeners = attachTo.binderListeners;
	if (binderListeners[event] === undefined) {
		binderListeners[event] = [];
		bindEvent(attachTo, event, eventProcessor(event, binderListeners));
	}
	binderListeners[event].push([selector, fn]);
}

function unlisten(selector, event, fn, attachTo) {
	attachTo = getAttachToElement(attachTo);
	var binderListeners = attachTo.binderListeners;
	binderListeners[event] = binderListeners[event].filter(function(listener) {
		return !(listener[0] === selector && listener[1] === fn);
	});
}

var liveListeners = [];
var liveRegistered = false;

function registerLiveListener(element, listener) {
	var attachElements = qa(listener.attachTo, element, true);
	attachElements.forEach(function(element) {
		listen(listener.selector, listener.event, listener.fn, element);
	});
}

function unregisterLiveListener(element, listener) {
	var attachElements = qa(listener.attachTo, element, true);
	attachElements.forEach(function(element) {
		unlisten(listener.selector, listener.event, listener.fn, element);
	});
}

function live(selector, event, fn, attachTo) {
	if (!liveRegistered) {
		onLoad(function(e) {
			liveListeners.forEach(function(listener) {
				registerLiveListener(e.memo, listener);
			});
		});

		onUnload(function(e) {
			liveListeners.forEach(function(listener) {
				unregisterLiveListener(e.memo, listener);
			});
		});
		liveRegistered = true;
	}
	var listener = {selector: selector, event: event, fn: fn, attachTo: attachTo};
	liveListeners.push(listener);
	registerLiveListener(document.body, listener);
}


function debounce(fn, delay) {
	var timer = null;
	function closure() {
		var args = arguments;
		clearTimeout(timer);
		timer = setTimeout(function () {
			fn.apply(null, args);
		}, delay);
	}
	function instant() {
		var args = arguments;
		clearTimeout(timer);
		fn.apply(null, args);
	}
	closure.instant = instant;
	return closure;
}


function q(selector, element) {
	if (element === undefined) {
		element = document;
	}
	return element.querySelector(selector);
}


function qa(selector, element, include_self) {
	if (element === undefined) {
		element = document;
	}
	var elements = ap.slice.call(element.querySelectorAll(selector));
	if (include_self) {
		if (element.matches(selector)) {
			elements.unshift(element);
		}
	}
	return elements;
}


function id(id, element) {
	var foundElement = document.getElementById(id);
	if (element === undefined) {
		return foundElement;
	}
	else {
		if (element.contains(foundElement)) {
			return foundElement;
		}
		else {
			return null;
		}
	}
}


function el(tagName) {
	var i, leni;
	var attrs = {};
	var contentIndex = 1;
	if (arguments.length > 1 && arguments[1].constructor === Object) {
		attrs = arguments[1];
		contentIndex = 2;
	}
	tagName = tagName.split(/(?=[\.#])/);
	var tag = document.createElement(tagName[0]);
	for (i = 1, leni = tagName.length; i < leni; i++) {
		var tagExtra = tagName[i];
		if (tagExtra[0] === '.') {
			tag.classList.add(tagExtra.slice(1));
		}
		else {
			tag.setAttribute('id', tagExtra.slice(1));
		}
	}

	for (var attrName in attrs) {
		if (has(attrs, attrName)) {
			tag.setAttribute(attrName, attrs[attrName]);
		}
	}

	for (i = contentIndex, leni = arguments.length; i < leni; i++) {
		var content = arguments[i];
		if (content === undefined) {
			continue;
		}
		if (typeof content === 'string') {
			tag.appendChild(document.createTextNode(content));
		}
		else {
			tag.appendChild(content);
		}
	}

	return tag;
}


function loaderJs() {
	var head = document.getElementsByTagName('head')[0];
	var loadedPaths;
	var registeredPaths = [];
	var waitingCallbacks = [];

	var scriptIsReady = function(state) {
		return (state === 'loaded' || state === 'complete' || state === 'uninitialized' || !state);
	};

	var fireCallbacks = function() {
		var firedCallbacks = [];
		waitingCallbacks.forEach(function(callback, i) {
			var fn = callback[0];
			var paths = callback[1];
			if (paths.every(function(path) { return loadedPaths.indexOf(path) !== -1; })) {
				firedCallbacks.push(i);
				setTimeout(fn, 0); // async call
			}
		});
		firedCallbacks.reverse();
		for (var i = 0; i < firedCallbacks.length; ++i) {
			waitingCallbacks.splice(firedCallbacks[i], 1);
		}
	};

	return function(paths, callback) {
		var missingPaths = [];
		if (loadedPaths === undefined) {
			loadedPaths = [];
			var scripts = qa('SCRIPT');
			scripts.forEach(function(script) {
				if (script.hasAttribute('src')) {
					loadedPaths.push(script.getAttribute('src'));
					registeredPaths.push(script.getAttribute('src'));
				}
			});
		}

		paths.forEach(function(path) {
			if (registeredPaths.indexOf(path) === -1) {
				missingPaths.push(path);
				registeredPaths.push(path);
			}
		});

		waitingCallbacks.push([callback, paths]);

		var loadMissingPath = function() {
			if (missingPaths.length === 0) {
				return;
			}
			var path = missingPaths[0];
			missingPaths = missingPaths.splice(1);
			var script = document.createElement('SCRIPT');
			script.src = path;
			script.onreadystatechange = script.onload = function(path) {
				return function() {
					if (scriptIsReady(script.readyState)) {
						loadedPaths.push(path);
						if (missingPaths.length === 0) {
							setTimeout(fireCallbacks, 0);
						}
						else {
							loadMissingPath();
						}
					}
				};
			}(path);
			head.appendChild(script);
		};

		loadMissingPath();

		setTimeout(fireCallbacks, 0);
	};
}


function loaderCss() {
	var loadedCss = {};
	return function(lib) {
		lib.forEach(function(source) {
			if (loadedCss[source] === undefined) {
				var link = el('link', {rel: 'stylesheet', type: 'text/css', href: source});
				document.getElementsByTagName('head')[0].appendChild(link);
				loadedCss[source] = true;
			}
		});
	};
}


window._utils2 = {
	checkFeatures: checkFeatures,
	getCookie: getCookie,
	setCookie: setCookie,
	has: has,
	lightCopy: lightCopy,
	forEachDict: forEachDict,
	dictToPairs: dictToPairs,
	pairsToDict: pairsToDict,
	encodeURLParameters: encodeURLParameters,
	triggerEvent: triggerEvent,
	bindEvent: bindEvent,
	unbindEvent: unbindEvent,
	onLoad: onLoad,
	onUnload: onUnload,
	triggerLoad: triggerLoad,
	triggerUnload: triggerUnload,
	unbindOnLoad: unbindOnLoad,
	listen: listen,
	unlisten: unlisten,
	live: live,
	debounce: debounce,
	q: q,
	qa: qa,
	id: id,
	el: el,
	loaderJs: new loaderJs(),
	loaderCss: new loaderCss()
};

}());

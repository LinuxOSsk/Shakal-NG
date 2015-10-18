(function () {

"use strict";

window._utils = {};

// features
var checkFeatures = function(features) {
	for (var i = 0; i < features.length; ++i) {
		switch (features[i]) {
			case "ajax":
				return window.XMLHttpRequest != undefined;
			case "history_push":
				return window.history && window.history.pushState;
			case "touch":
				return "ontouchstart" in window;
			default:
				return false;
		}
	}
	return true;
};

window._utils.checkFeatures = checkFeatures;

// cookies
var getCookie = function(name, defaultVal) {
	var cookieValue = defaultVal;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
};

var setCookie = function(name, value, days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
};

window._utils.getCookie = getCookie;
window._utils.setCookie = setCookie;


// scroll
var findVerticalPos = function(obj) {
	var curtop = 0;
	if (obj.offsetParent) {
		do {
			curtop += obj.offsetTop;
		} while (obj = obj.offsetParent);
		return [curtop];
	}
};

var scrollToElement = function(element) {
	if (window.scroll) {
		var posOffset = 0;
		if (window.innerHeight !== undefined) {
			posOffset = window.innerHeight / 2;
		}
		window.scroll(0, Math.max(window.findVerticalPos(element) - posOffset, 0));
	}
};

var getScroll = function(){
	if(window.pageYOffset != undefined){
		return [pageXOffset, pageYOffset];
	}
	else {
		var sx, sy;
		var d = document.documentElement;
		var b = document.body;
		sx = d.scrollLeft || b.scrollLeft || 0;
		sy = d.scrollTop || b.scrollTop || 0;
		return [sx, sy];
	}
};

window._utils.findVerticalPos = findVerticalPos;
window._utils.scrollToElement = scrollToElement;
window._utils.getScroll = getScroll;


// debounce
var debounce = function(fn, delay) {
	var timer = null;
	return function () {
		var context = this, args = arguments;
		clearTimeout(timer);
		timer = setTimeout(function () {
			fn.apply(context, args);
		}, delay);
	};
};

window._utils.debounce = debounce;


// iteration
if (Array.prototype.forEach) {
	var coreForEach = Array.prototype.forEach;
	var forEach = function(collection, fn) {
		coreForEach.call(collection, fn);
	}
}
else {
	var forEach = function(collection, fn) {
		for (var i = 0, len = collection.length; i < len; i++) {
			fn(collection[i], i);
		}
	};
}

if (Array.prototype.filter) {
	var filter = function(array, fun) {
		return array.filter(fun);
	}
}
else {
	var filter = function(array, fun) {
		var res = [];
		forEach(array, function(val) {
			if (fun.call(val)) {
				res.push(val);
			}
		});
	}
}

if (Array.prototype.some) {
	var some = function(array, test) {
		return array.some(test);
	}
}
else {
	var some = function(array, test) {
		var ret = false;

		for (var i = 0, len = array.length; i < len; i++) {
			ret = ret || fn(array[i], i);
			if (ret) {
				break;
			}
		}
		return ret;
	}
}

if (Array.prototype.every) {
	var every = function(array, test) {
		return array.every(test);
	}
}
else {
	var some = function(array, test) {
		var ret = true;

		for (var i = 0, len = array.length; i < len; i++) {
			ret = ret && fn(array[i], i);
			if (!ret) {
				break;
			}
		}
		return ret;
	}
}

window._utils.forEach = forEach;
window._utils.filter = filter;
window._utils.some = some;
window._utils.every = every;

// forms
var serializeForm = function(formElement, raw) {
	var q = [];
	if (raw) {
		var addParameter = function(name, value) {
			q.push([name, value]);
		}
	}
	else {
		var addParameter = function(name, value) {
			q.push(name + '=' + encodeURIComponent(value));
		}
	}

	var elements = formElement.elements;
	_utils.forEach(elements, function(element) {
		if (element.name == '' || element.disabled) {
			return;
		}

		switch (element.nodeName.toLowerCase()) {
			case 'input':
				switch (element.type) {
					case 'text':
					case 'hidden':
					case 'password':
					case 'button':
					case 'number':
					case 'email':
						addParameter(element.name, element.value);
						break;
					case 'checkbox':
					case 'radio':
						if (element.checked) {
							addParameter(element.name, element.value);
						}
						break;
					case 'file':
					case 'reset':
					case 'submit':
						break;
				}
				break;
			case 'textarea':
				addParameter(element.name, element.value);
				break;
			case 'select':
				switch (element.type) {
					case 'select-one':
						addParameter(element.name, element.value);
						break;
					case 'select-multiple':
						_utils.forEach(formElement.options, function(option) {
							if (option.selected) {
								addParameter(element.name, option.value);
							}
						});
						break;
				}
				break;
			case 'button':
				break;
		}
	});

	if (raw) {
		return q;
	}
	else {
		return q.join('&');
	}
};

var getUrlParameterByName = function(name, url) {
	var location = url || window.location;
	var name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
	var results = regex.exec(location);
	return results === null ? null : decodeURIComponent(results[1].replace(/\+/g, " "));
};

window._utils.serializeForm = serializeForm;
window._utils.getUrlParameterByName = getUrlParameterByName;

// events
var triggerEvent = function(element, name, memo) {
	var event;
	if (document.createEvent) {
		event = document.createEvent('HTMLEvents');
		event.initEvent(name, true, true);
	}
	else {
		event = document.createEventObject();
		event.eventType = name;
	}

	event.eventName = name;
	event.memo = memo || { };

	if (document.createEvent) {
		element.dispatchEvent(event);
	}
	else {
		element.fireEvent("on" + event.eventType, event);
	}
};

var bindEvent = function(element, name, fn) {
	if (document.addEventListener) {
		element.addEventListener(name, fn, false);
	}
	else {
		element.attachEvent('on' + name, fn);
	}
};

var unbindEvent = function(element, name, fn) {
	if (document.removeEventListener) {
		element.removeEventListener(name, fn, false);
	}
	else {
		element.detachEvent('on' + name, fn);
	}

}

window._utils.triggerEvent = triggerEvent;
window._utils.bindEvent = bindEvent;
window._utils.unbindEvent = unbindEvent;

// dom
var el = document.createElement('DIV');

var insertAfter = function(newNode, referenceNode) {
	referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
};

var onLoad = function(callback) {
	callback({memo: document.body});
	window._utils.bindEvent(document.body, 'contentloaded', callback);
};

var triggerLoad = function(element) {
	window._utils.triggerEvent(document.body, 'contentloaded', element);
};

var isInPage = function(element) {
	return document.body.contains(element);
};

if (el.classList == undefined) {
	var hasClass = function(elem, cls) {
		return elem.className.split(" ").indexOf(cls) !== -1;
	}

	var addClass = function(elem, cls) {
		elem.className += " " + cls;
	}

	var removeClass = function(elem, cls) {
		var classNames = elem.className.split(" ");
		var newClassNames = [];
		for (var i = 0, leni = classNames.length; i < leni; i++) {
			if (classNames[i] != cls) {
				newClassNames.push(classNames[i]);
			}
		}
		elem.className = newClassNames.join(" ");
	}

	var toggleClass = function(elem, cls) {
		if (hasClass(elem, cls)) {
			removeClass(elem, cls);
		}
		else {
			addClass(elem, cls);
		}
	}
}
else {
	var hasClass = function(elem, cls) {
		return elem.classList.contains(cls);
	}

	var addClass = function(elem, cls) {
		return elem.classList.add(cls);
	}

	var removeClass = function(elem, cls) {
		return elem.classList.remove(cls);
	}

	var toggleClass = function(elem, cls) {
		return elem.classList.toggle(cls);
	}
}

if (el.getElementsByClassName == undefined) {
	var getElementsByClassName = function(parent, cls) {
		var elements = parent.getElementsByTagName('*');
		var match = [];
		for (var i = 0, leni = elements.length; i < leni; i++) {
			if (hasClass(elements[i], cls)) {
				match.push(elements[i]);
			}
		}
		return match;
	}
}
else {
	var getElementsByClassName = function(parent, cls) {
		return parent.getElementsByClassName(cls);
	}
}

var byId = function(elementId) {
	return document.getElementById(elementId);
};

var createDiv = function(className, id) {
	var div = document.createElement('DIV');
	if (className !== undefined) {
		div.className = className;
	}
	if (id !== undefined) {
		div.setAttribute('id', id);
	}
	return div;
};

window._utils.insertAfter = insertAfter;
window._utils.onLoad = onLoad;
window._utils.triggerLoad = triggerLoad;
window._utils.isInPage = isInPage;
window._utils.hasClass = hasClass;
window._utils.addClass = addClass;
window._utils.removeClass = removeClass;
window._utils.toggleClass = toggleClass;
window._utils.cls = getElementsByClassName;
window._utils.id = byId;
window._utils.createDiv = createDiv;

var loaderJs = (function () {
	var head = document.getElementsByTagName('head')[0];
	var loadedPaths = [];
	var registeredPaths = [];
	var waitingCallbacks = [];

	var scriptIsReady = function(state) {
		return (state === 'loaded' || state === 'complete' || state === 'uninitialized' || !state);
	}

	var fireCallbacks = function() {
		var firedCallbacks = [];
		forEach(waitingCallbacks, function(callback, i) {
			var fn = callback[0];
			var paths = callback[1];
			if (every(paths, function(path) { return loadedPaths.indexOf(path) !== -1; })) {
				firedCallbacks.push(i);
				fn();
			}
		});
		firedCallbacks.reverse();
		for (var i = 0; i < firedCallbacks.length; ++i) {
			waitingCallbacks.splice(firedCallbacks[i], 1);
		}
	};

	return function(paths, callback) {
		var missingPaths = [];

		forEach(paths, function(path) {
			if (registeredPaths.indexOf(path) === -1) {
				missingPaths.push(path);
				registeredPaths.push(path);
			}
		});

		waitingCallbacks.push([callback, paths]);

		forEach(missingPaths, function(path) {
			var script = document.createElement('SCRIPT');
			script.src = path;
			script.onreadystatechange = script.onload = function(path) {
				return function() {
					if (scriptIsReady(script.readyState)) {
						loadedPaths.push(path);
						fireCallbacks();
					}
				};
			}(path);
			head.appendChild(script);
		});

		setTimeout(fireCallbacks, 0);
	}
}());

window._utils.loaderJs = loaderJs;


}());

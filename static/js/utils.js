(function () {

"use strict";

window._utils = {};

// features
var checkFeatures = function(features) {
	for (var i = 0; i < features.length; ++i) {
		switch (features[i]) {
			case "ajax":
				return window.XMLHttpRequest !== undefined;
			case "history_push":
				return window.history && window.history.pushState;
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
};

window._utils.checkFeatures = checkFeatures;

// cookies
var getCookie = function(name, defaultVal) {
	var cookieValue = defaultVal;
	if (document.cookie && document.cookie !== '') {
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
	var expires;
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		expires = '; expires='+date.toGMTString();
	}
	else {
		expires = '';
	}
	document.cookie = name+'='+value+expires+'; path=/';
};

window._utils.getCookie = getCookie;
window._utils.setCookie = setCookie;


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
var forEach;
if (Array.prototype.forEach) {
	var coreForEach = Array.prototype.forEach;
	forEach = function(collection, fn) {
		coreForEach.call(collection, fn);
	};
}
else {
	forEach = function(collection, fn) {
		for (var i = 0, len = collection.length; i < len; i++) {
			fn(collection[i], i);
		}
	};
}

var filter;
if (Array.prototype.filter) {
	filter = function(array, fun) {
		return array.filter(fun);
	};
}
else {
	filter = function(array, fun) {
		var res = [];
		forEach(array, function(val) {
			if (fun.call(val)) {
				res.push(val);
			}
		});
	};
}

var some;
if (Array.prototype.some) {
	some = function(array, test) {
		return array.some(test);
	};
}
else {
	some = function(array, test) {
		var ret = false;

		for (var i = 0, len = array.length; i < len; i++) {
			ret = ret || fn(array[i], i);
			if (ret) {
				break;
			}
		}
		return ret;
	};
}

var every;
if (Array.prototype.every) {
	every = function(array, test) {
		return array.every(test);
	};
}
else {
	every = function(array, test) {
		var ret = true;

		for (var i = 0, len = array.length; i < len; i++) {
			ret = ret && fn(array[i], i);
			if (!ret) {
				break;
			}
		}
		return ret;
	};
}

window._utils.forEach = forEach;
window._utils.filter = filter;
window._utils.some = some;
window._utils.every = every;


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

};

window._utils.triggerEvent = triggerEvent;
window._utils.bindEvent = bindEvent;
window._utils.unbindEvent = unbindEvent;

// dom
var el = document.createElement('DIV');

var insertAfter = function(newNode, referenceNode) {
	referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
};

var onLoad = function(callback) {
	if (document.body === null) {
		window._utils.bindEvent(document, 'DOMContentLoaded', function() {
			callback({memo: document.body});
			window._utils.bindEvent(document.body, 'contentloaded', callback);
		});
	}
	else {
		callback({memo: document.body});
		window._utils.bindEvent(document.body, 'contentloaded', callback);
	}
};

var triggerLoad = function(element) {
	window._utils.triggerEvent(document.body, 'contentloaded', element);
};

var isInPage = function(element) {
	return document.body.contains(element);
};

var has = function(array, key) {
	return Object.prototype.hasOwnProperty.call(array, key);
};

var hasClass, addClass, removeClass, toggleClass;
if (el.classList === undefined) {
	hasClass = function(elem, cls) {
		return elem.className.split(" ").indexOf(cls) !== -1;
	};

	addClass = function(elem, cls) {
		elem.className += " " + cls;
	};

	removeClass = function(elem, cls) {
		var classNames = elem.className.split(" ");
		var newClassNames = [];
		for (var i = 0, leni = classNames.length; i < leni; i++) {
			if (classNames[i] != cls) {
				newClassNames.push(classNames[i]);
			}
		}
		elem.className = newClassNames.join(" ");
	};

	toggleClass = function(elem, cls) {
		if (hasClass(elem, cls)) {
			removeClass(elem, cls);
		}
		else {
			addClass(elem, cls);
		}
	};
}
else {
	hasClass = function(elem, cls) {
		return elem.classList.contains(cls);
	};

	addClass = function(elem, cls) {
		return elem.classList.add(cls);
	};

	removeClass = function(elem, cls) {
		return elem.classList.remove(cls);
	};

	toggleClass = function(elem, cls) {
		return elem.classList.toggle(cls);
	};
}

var getElementsByClassName;
if (el.getElementsByClassName === undefined) {
	getElementsByClassName = function(parent, cls) {
		var elements = parent.getElementsByTagName('*');
		var match = [];
		for (var i = 0, leni = elements.length; i < leni; i++) {
			if (hasClass(elements[i], cls)) {
				match.push(elements[i]);
			}
		}
		return match;
	};
}
else {
	getElementsByClassName = function(parent, cls) {
		return parent.getElementsByClassName(cls);
	};
}

var byId = function(elementId) {
	return document.getElementById(elementId);
};

var byTag = function(element, tagName) {
	return element.getElementsByTagName(tagName);
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

var escapeHTML = function(text) {
	return text
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;");
};

var escapeHTMLAttr = function(text) {
	return escapeHTML(text)
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
};

var elem = function(elementName, attrs, content) {
	var element = document.createElement(elementName);
	if (attrs !== undefined) {
		for (var attrName in attrs) {
			if (has(attrs, attrName)) {
				element.setAttribute(attrName, attrs[attrName]);
			}
		}
	}

	if (content !== undefined) {
		element.appendChild(document.createTextNode(content));
	}
	return element;
};

window._utils.insertAfter = insertAfter;
window._utils.onLoad = onLoad;
window._utils.triggerLoad = triggerLoad;
window._utils.isInPage = isInPage;
window._utils.has= has;
window._utils.hasClass = hasClass;
window._utils.addClass = addClass;
window._utils.removeClass = removeClass;
window._utils.toggleClass = toggleClass;
window._utils.cls = getElementsByClassName;
window._utils.id = byId;
window._utils.tag = byTag;
window._utils.createDiv = createDiv;
window._utils.escapeHTML = escapeHTML;
window._utils.escapeHTMLAttr = escapeHTMLAttr;
window._utils.elem = elem;

var loaderJs = (function () {
	var head = document.getElementsByTagName('head')[0];
	var loadedPaths = [];
	var registeredPaths = [];
	var waitingCallbacks = [];

	var scriptIsReady = function(state) {
		return (state === 'loaded' || state === 'complete' || state === 'uninitialized' || !state);
	};

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
	};
}());

window._utils.loaderJs = loaderJs;

var filesizeformat = function(bytes) {
	var KB = 1 << 10;
	var MB = 1 << 20;
	var GB = 1 << 30;
	var TB = 1 << 40;
	var PB = 1 << 50;

	var formatFloat = function(val) {
		return (Math.round(val * 100.0)) / 100.0;
	};

	if (bytes < KB) {
		return bytes + ' B';
	}
	else if (bytes < MB) {
		return formatFloat(bytes / KB) + ' KB';
	}
	else if (bytes < GB) {
		return formatFloat(bytes / MB) + ' MB';
	}
	else if (bytes < TB) {
		return formatFloat(bytes / GB) + ' GB';
	}
	else {
		return formatFloat(bytes / PB) + ' PB';
	}
};

window._utils.filesizeformat = filesizeformat;


}());

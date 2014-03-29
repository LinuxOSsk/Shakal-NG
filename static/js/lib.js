// Cookies

function setCookie(name, value, days) {
	var expires = "";
	if (days) {
		var date = new Date();
		date.setTime(date.getTime() + (days*24*60*60*1000));
		expires = "; expires=" + date.toGMTString();
	}
	document.cookie = name + "="+encodeURIComponent(value) + expires + "; path=/";
}

function getCookie(name) {
	var cookieName = name + "=";
	var cookies = document.cookie.split(';');
	for(var i = 0; i < cookies.length; i++) {
		var c = cookies[i];
		while (c.charAt(0)==' ') c = c.substring(1, c.length);
		if (c.indexOf(cookieName) == 0) {
			return decodeURIComponent(c.substring(cookieName.length, c.length));
		}
	}
	return null;
}

function deleteCookie(name) {
	setCookie(name, "", -1);
}

var supersleight= function() {
	var out = document.getElementById('out');
	var root = false;
	var applyPositioning = true;

	var shim	= '/static/2013/images/empty.gif';

	var fnLoadPngs = function() {
		if (root) {
			root = document.getElementById(root);
		}else{
			root = document;
		}
		for (var i = root.all.length - 1, obj = null; (obj = root.all[i]); i--) {
			out.innerHTML += '<br>a';
			if (obj.currentStyle.backgroundImage.match(/\.png/i) !== null) {
				bg_fnFixPng(obj);
			}
			if (obj.tagName=='IMG' && obj.src.match(/\.png$/i) !== null){
				el_fnFixPng(obj);
			}
			if (applyPositioning && (obj.tagName=='A' || obj.tagName=='INPUT') && obj.style.position === ''){
				obj.style.position = 'relative';
			}
		}
	};

	var bg_fnFixPng = function(obj) {
		var mode = 'scale';
		var bg	= obj.currentStyle.backgroundImage;
		var src = bg.substring(5,bg.length-2);
		if (obj.currentStyle.backgroundRepeat == 'no-repeat') {
			mode = 'crop';
		}
		obj.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + src + "', sizingMethod='" + mode + "')";
		obj.style.backgroundImage = 'url('+shim+')';
	};

	var el_fnFixPng = function(img) {
		var src = img.src;
		img.style.width = img.width + "px";
		img.style.height = img.height + "px";
		img.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + src + "', sizingMethod='scale')";
		img.src = shim;
	};

	return {
		init: function() {
			fnLoadPngs();
		}
	};
}();

supersleight.init();

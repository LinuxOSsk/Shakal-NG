(function(_) {
"use strict";

var register = function(root) {
	_.forEach(_.cls(root, 'attachment-upload'), function(uploadElement) {
	});
};

_.onLoad(function(e) { register(e.memo); });

}(_utils));

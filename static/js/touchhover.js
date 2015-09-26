(function (_) {

var register = function(root) {
	if (!_.checkFeatures(['touch'])) {
		return;
	}

	var toggleHover = function() {
		if (_.hasClass(this, 'touchhover')) {
			_.removeClass(this, 'touchhover')
			_.forEach(_.cls(this, 'touchhover'), function(element) {
				_.removeClass(element, 'touchhover');
			});
		}
		else {
			_.addClass(this, 'touchhover')
		}
	};

	_.forEach(_.cls(root, 'touchhover-emul'), function(element) {
		_.removeClass(element, 'touchhover-emul');
		element.onclick = toggleHover;
	});
};

_.onLoad(register);

}(window._utils));

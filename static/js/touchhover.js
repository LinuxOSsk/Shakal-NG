(function (_) {

var register = function(root) {
	/*
	if (!_.checkFeatures(['touch'])) {
		return;
	}
	*/

	var toggleHover = function(event) {
		if (_.hasClass(this, 'touchhover')) {
			_.removeClass(this, 'touchhover');
			_.forEach(_.cls(this, 'touchhover'), function(element) {
				_.removeClass(element, 'touchhover');
			});
		}
		else {
			_.addClass(this, 'touchhover');
			event.preventDefault();
		}
	};

	_.forEach(_.cls(root, 'touchhover-emul'), function(element) {
		_.removeClass(element, 'touchhover-emul');
		_.bindEvent(element, 'click', toggleHover);
	});
};

_.onLoad(function(e) { register(e.memo); });

}(window._utils));

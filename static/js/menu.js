(function(_) {

var registerUserPanel = function(root) {
	var userPanel = _.id(root, 'user_panel');
	if (userPanel === null || !_.hasClass(userPanel, 'touchhover-emul')) {
		return;
	}
	var user = _.cls(userPanel, 'user')[0];
	if (user === undefined) {
		return;
	}
	_.removeClass(userPanel, 'touchhover-emul');

	_.bindEvent(user, 'click', function(event) {
		if (event.which !== 1) {
			return;
		}
		_.toggleClass(userPanel, 'touchhover');
		event.preventDefault();
	});
};

_.onLoad(function(e) { registerUserPanel(e.memo); });

}(_utils));

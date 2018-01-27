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

var copyMenu = function(root) {
	if (root !== document.body) {
		return;
	}

	var clone;
	var menuPanel = _.id('menu_panel');
	var searchPanel = _.id('search_panel');
	var blockLinux = _.id('module_block_linux');
	var blockPortal = _.id('module_block_portal');
	if (menuPanel === null || searchPanel === null || blockLinux === null || blockPortal === null) {
		return;
	}

	clone = blockPortal.cloneNode(true);
	clone.setAttribute('id', clone.getAttribute('id') + '_clone');
	menuPanel.insertBefore(clone, searchPanel);

	clone = blockLinux.cloneNode(true);
	clone.setAttribute('id', clone.getAttribute('id') + '_clone');
	menuPanel.insertBefore(clone, searchPanel);
};

_.onLoad(function(e) {
	registerUserPanel(e.memo);
	copyMenu(e.memo);
});

var onClick = function(e) {
	if (e.which !== 1) {
		return;
	}
	var target = e.target || e.srcElement;

	while (target) {
		if (_.hasClass(target, 'toggle-menu-action')) {
			_.toggleClass(document.body, 'visible-menu');
			e.preventDefault();
			return;
		}
		target = target.parentNode;
		if (!(target instanceof Element)) {
			return;
		}
	}
};

_.bindEvent(document.body, 'click', onClick);

}(_utils));

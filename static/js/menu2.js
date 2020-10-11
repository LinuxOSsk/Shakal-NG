(function(_) {


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
	copyMenu(e.memo);
});


}(_utils2));

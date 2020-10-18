(function(_) {


function registerTouchhover(root) {
	_.qa('.touchhover-emul', root).forEach(function (element) {
		element.classList.remove('touchhover-emul');
		element.classList.add('touchhover-emul-js');
	});
}


function onTouchHoverEmulClicked(e, element) {
	if (e.which !== 1) { return; }
	element.classList.toggle('touchhover');
	var target = e.target;
	while (target) {
		if (target === element || target.classList.contains('notouch')) {
			e.preventDefault();
			return;
		}
		if (target.tagName.toLowerCase() === 'a') {
			return;
		}
		target = target.parentNode;
	}
}


function onBodyClicked(e) {
	if (e.which !== 1) { return; }
	var target = e.target;
	_.qa('.touchhover-emul-js.touchhover').forEach(function(element) {
		if (target !== element && !element.contains(target)) {
			element.classList.remove('touchhover');
		}
	});
}


function copyMenu(root) {
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
}

_.onLoad(function(e) {
	registerTouchhover(e.memo);
	copyMenu(e.memo);
});

_.listen('.touchhover-emul-js', 'click', onTouchHoverEmulClicked);
_.listen(null, 'click', onBodyClicked);


}(_utils2));

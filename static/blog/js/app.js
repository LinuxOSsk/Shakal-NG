(function(_) {


var body = document.body;


function closeOpened(event) {
	var target = event.target;
	_.qa('.dropdown.menu.open').forEach(function(menu) {
		if (menu === target || menu.contains(target)) {
			return;
		}
		menu.classList.remove('open');
	});
}

function processToggleClick(event) {
	if (event.which !== 1) {
		return;
	}
	var element = event.target;
	if (!element.matches('[data-toggle-target]')) {
		element = element.closest('[data-toggle-target]');
	}
	var toggle = element.dataset.toggleTarget;
	var toggleClass = element.dataset.toggleClass || 'toggled';
	_.qa(toggle).forEach(function(element) { element.classList.toggle(toggleClass); });
	event.preventDefault();
	event.stopPropagation();
}

function onLoaded(element) {
	if (element === body) {
		setTimeout(function() {
			body.classList.remove('no-animate');
		}, 2000);
	}
}

function disableAnimation() {
	body.classList.add('no-animate');
}

function enableAnimation() {
	body.classList.remove('no-animate');
}


_.onLoad(function(e) { onLoaded(e.memo); });
_.bindEvent(document.body, 'click', closeOpened);
_.listen('[data-toggle-target]', 'click', processToggleClick);


}(_utils2));

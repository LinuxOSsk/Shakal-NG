(function(_) {


function onParentLinkClicked(e, element) {
	if (e.which !== 1) {
		return;
	}

	e.preventDefault();

	var parentElement = _.id(element.getAttribute('href').slice(1));
	if (parentElement === null) {
		return;
	}

	var container = parentElement.closest('.comment-container');
	if (container === null) {
		return;
	}

	_.modalOpen(container.cloneNode(true), {className: 'full'});
}


_.listen('.comment_info > .parent-link', 'click', onParentLinkClicked);


}(_utils2));

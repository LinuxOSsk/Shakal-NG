(function(_) {

function onDeleteMessageClicked(e, element) {
	if (e.which !== 1) {
		return;
	}
	var listItem = element.closest('li');
	listItem.parentNode.removeChild(listItem);
}

_.live('.delete-action', 'click', onDeleteMessageClicked, 'ul.messages');

}(window._utils2));

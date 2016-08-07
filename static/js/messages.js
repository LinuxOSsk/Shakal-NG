(function(_) {

var registerMessage = function(element) {
	var deleteAction = document.createElement('A');
	deleteAction.className = 'delete-action';
	deleteAction.setAttribute('href', '#');
	deleteAction.appendChild(document.createTextNode('⨉'));
	deleteAction.onclick = function() {
		element.parentNode.removeChild(element);
		return false;
	};
	element.appendChild(deleteAction);
};

var register = function(root) {
	_.forEach(_.cls(root, 'messages'), function(element) {
		if (element.tagName.toUpperCase() !== 'UL') {
			return;
		}
		_.forEach(_.tag(element, 'LI'), registerMessage);
	});
};

_.onLoad(function(e) { register(e.memo); });

}(window._utils));

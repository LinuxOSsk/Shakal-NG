function checkAttribute(element, attribute) {
	var el = document.createElement(element);
	if (attribute in el) {
		return true;
	}
	else {
		return false;
	}
}

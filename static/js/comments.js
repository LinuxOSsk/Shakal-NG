(function(_) {


var E = _.el;
var timeout;


function onParentLinkClicked(e, element) {
	if (e.which !== 1) {
		return;
	}

	var parentElement = _.id(element.getAttribute('href').slice(1));
	if (parentElement === null) {
		return;
	}

	var container = parentElement.closest('.comment-container');
	if (container === null) {
		return;
	}

	_.modalOpen(container.cloneNode(true), {className: 'full'});
	e.preventDefault();
}


function onParentMouseOver(e, element) {
	if (element.closest('.comment-tooltip') !== null) {
		return;
	}
	var container = element.closest('.comments_tree');
	var parentElement = _.id(element.getAttribute('href').slice(1));
	var currentElement = element.closest('.comment-container');
	if (container === null || parentElement === null || currentElement === null) {
		return;
	}
	parentElement = parentElement.closest('.comment-container');
	if (parentElement === null) {
		return;
	}
	var tooltip = _.q('.comment-tooltip', container);
	if (tooltip === null) {
		tooltip = E('div.comment-tooltip.tooltip.closed',
			E('div.tooltip-bubble', E('div.tooltip-content'))
		);
	}
	var tooltipContent = _.q('.tooltip-content', tooltip);

	tooltipContent.innerHTML = '';
	tooltipContent.appendChild(parentElement.cloneNode(true));
	currentElement.parentNode.insertBefore(tooltip, currentElement.parentNode.firstChild);

	if (timeout !== undefined) {
		clearTimeout(timeout);
	}
	timeout = setTimeout(function() {
		tooltip.classList.remove('closed');
	}, 500);
}


function onParentMouseOut(e, element) {
	if (element.closest('.comment-tooltip') !== null) {
		return;
	}
	if (timeout !== undefined) {
		clearTimeout(timeout);
		timeout = undefined;
	}
	var container = element.closest('.comments_tree');
	var tooltip = _.q('.comment-tooltip', container);
	if (tooltip !== null) {
		tooltip.classList.add('closed');
	}
}


_.listen('.comment_info > .parent-link', 'click', onParentLinkClicked);
_.live('.comment_info > .parent-link', 'mouseover', onParentMouseOver, '.comments_tree');
_.live('.comment_info > .parent-link', 'mouseout', onParentMouseOut, '.comments_tree');


}(_utils2));

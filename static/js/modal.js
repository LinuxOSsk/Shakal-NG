(function(_) {


var E = _.el;
var modalContainer;
var closeAnimationMaxDuration = 1000;


function getTopLevelModal() {
	if (modalContainer === null) {
		return;
	}
	var windows = _.qa(':scope > .modal-overlay.open', modalContainer);
	if (windows.length) {
		return windows[windows.length-1];
	}
	else {
		return null;
	}
}


function modalOpen(content, options) {
	if (modalContainer === undefined) {
		modalContainer = _.el('div.modals');
		document.body.appendChild(modalContainer);
	}

	var contentContainer, header, titleElement;
	options = options || {};
	var modal = E('div.modal-overlay',
		E('div.modal-window',
			header=E('div.modal-header', titleElement=E('div.modal-title.empty'), E('button.modal-close')),
			contentContainer=E('div.modal-content')
		)
	);

	if (typeof content === 'string') {
		contentContainer.innerHTML = content;
	}
	else {
		contentContainer.appendChild(content);
	}
	if (options.title !== undefined) {
		titleElement.classList.remove('empty');
		titleElement.appendChild(document.createTextNode(options.title));
	}
	var withClassElement = _.q(':scope > [data-modal-class]', contentContainer);
	if (withClassElement !== null) {
		modal.className += ' ' + withClassElement.dataset.modalClass;
	}
	if (options.className !== undefined) {
		modal.className += ' ' + options.className;
	}

	modalContainer.appendChild(modal);
	_.triggerLoad(modal);
	setTimeout(function() {
		if (!modal.classList.contains('close')) {
			modal.classList.add('open');
			document.body.classList.add('modal-open');
		}
	}, 10);
	return modal;
}


function modalClose(modalElement) {
	var modal = modalElement;
	if (!modal.classList.contains('modal-overlay')) {
		modal = modal.closest('.modal-overlay');
	}
	if (modal === null || !modal.classList.contains('open')) {
		return;
	}
	modal.classList.remove('open');
	modal.classList.add('close');
	_.triggerUnload(modal);

	if (getTopLevelModal() === null) {
		document.body.classList.remove('modal-open');
	}

	setTimeout(function() { modal.parentNode.removeChild(modal); }, closeAnimationMaxDuration);
}


function processModalAjaxClick(e, link) {
	if (e.which !== 1) {
		return;
	}

	var url = link.getAttribute('href');
	_.xhrSend({
		url: url,
		successFn: function(response) {
			modalOpen(response);
		}
	});
	e.preventDefault();
}


function processModalCloseClick(e, elem) {
	if (e.which !== 1) {
		return;
	}

	modalClose(elem);
	e.preventDefault();
}


function processModalOverlayClick(e, elem) {
	if (e.which !== 1 || !e.target.classList.contains('modal-overlay')) {
		return;
	}

	modalClose(elem);
}


function processOpenInsideModal(e, elem) {
	var modal = elem.closest('.modal-overlay');
	if (e.which !== 1 || modal === null) {
		return;
	}
	var url = elem.getAttribute('href');
	if (!url || url[0] === '#') {
		return;
	}

	_.xhrSend({
		url: url,
		successFn: function(response) {
			var contentContainer = _.q('.modal-content', modal);
			_.triggerUnload(contentContainer);
			contentContainer.innerHTML = response;
			_.triggerLoad(contentContainer);
		}
	});
	e.preventDefault();
}


function processKeydown(e) {
	// Close on escape
	if (e.keyCode !== 27 || modalContainer === undefined) {
		return;
	}

	var topLevelModalWindow = getTopLevelModal();
	if (topLevelModalWindow !== null) {
		modalClose(topLevelModalWindow);
		e.preventDefault();
	}
}


_.listen('.modal-ajax', 'click', processModalAjaxClick);
_.listen('.modal-close', 'click', processModalCloseClick);
_.listen('.modal-overlay.open', 'click', processModalOverlayClick);
_.listen('.open-inside-modal', 'click', processOpenInsideModal);
_.listen('body', 'keydown', processKeydown);
_.modalOpen = modalOpen;


}(_utils2));

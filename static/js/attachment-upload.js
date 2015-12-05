(function(_) {
"use strict";

// http://stackoverflow.com/questions/14069421/show-an-image-preview-before-upload
// http://www.sitepoint.com/html5-javascript-file-upload-progress-bar/
// https://developer.mozilla.org/en-US/docs/Using_files_from_web_applications

var createUploader = function(element) {
	var uploadAjax = _.cls(element, 'attachment-upload-ajax')[0];
	if (uploadAjax === undefined) {
		return;
	}
	var attachmentTemplate = _.cls(uploadAjax, 'attachment-template')[0];
	if (attachmentTemplate === undefined) {
		return;
	}

	_.addClass(element, 'ajax');

	var urls = {
		list: uploadAjax.getAttribute('data-list-url')
	};

	var previews = [];
	var updatePreviews = function() {
		_.forEach(previews, function(preview) {
			preview.element.parentNode.removeChild(preview.element);
		});
		previews = [];

		_.xhrSend({
			url: urls.list,
			successFn: function(data) {
				_.forEach(data, function(preview) {
					var element = attachmentTemplate.cloneNode(true);
					_.removeClass(element, 'attachment-template');
					attachmentTemplate.parentNode.insertBefore(element, attachmentTemplate);
					previews.push({
						element: element
					});
				});
			}
		});
	};

	updatePreviews();
};


var register = function(root) {
	if (!_.checkFeatures(["ajax", "drop", "file"])) {
		return;
	}

	_.forEach(_.cls(root, 'attachment-upload'), function(uploadElement) {
		createUploader(uploadElement);
	});
};

_.onLoad(function(e) { register(e.memo); });

}(_utils));

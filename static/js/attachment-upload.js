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

	var createPreview = function(data) {

		var element = attachmentTemplate.cloneNode(true);

		_.removeClass(element, 'attachment-template');

		if (data.thumbnails !== undefined && data.thumbnails.standard !== undefined) {
			var thumbnailTemplate = _.cls(element, 'template-thumbnail')[0];
			if (thumbnailTemplate !== undefined) {
				var style = thumbnailTemplate.getAttribute('data-style');
				var img = _.elem('IMG', {src: data.thumbnails.standard});
				if (style !== undefined) {
					img.setAttribute('style', style);
				}
				thumbnailTemplate.appendChild(img);
			}
		}

		attachmentTemplate.parentNode.insertBefore(element, attachmentTemplate);
		previews.push({
			element: element
		});
	};

	var updatePreviews = function() {
		_.forEach(previews, function(preview) {
			preview.element.parentNode.removeChild(preview.element);
		});
		previews = [];

		_.xhrSend({
			url: urls.list,
			successFn: function(data) {
				_.forEach(data, function(preview) {
					createPreview(preview);
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

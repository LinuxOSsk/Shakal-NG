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
	var uploadContainer = _.cls(element, 'attachment-upload-container')[0];
	var uploadInput = _.cls(element, 'attachment-upload')[0];
	if (attachmentTemplate === undefined || uploadContainer === undefined || uploadInput === undefined) {
		return;
	}

	_.addClass(element, 'ajax');
	uploadInput.style.visibility = 'hidden';
	uploadInput.style.display = 'block';
	uploadInput.style.width = '1px';
	uploadInput.style.height = '1px';
	uploadInput.style.position = 'absolute';

	var urls = {
		list: uploadAjax.getAttribute('data-list-url')
	};

	var uploadFile = function(fileObject) {
		var mimetype = fileObject.type;
		var previewData = {
			name: fileObject.name,
			filesize: fileObject.size,
			persistent: true
		};
		var preview = createPreview(previewData);
		if (mimetype === 'image/jpeg' || mimetype === 'image/png') {
			var reader = new FileReader();
			reader.onload = function(e) {
				preview.img.setAttribute('src', e.target.result);
				preview.img.style.display = 'block';
			};
			reader.readAsDataURL(fileObject);
		}
	};

	var onUploadChanged = function() {
		_.unbindEvent(uploadInput, 'change');
		_.forEach(uploadInput.files, function(fileObject) {
			uploadFile(fileObject);
		});
		var newInput = uploadInput.cloneNode(true);
		uploadInput.parentNode.insertBefore(newInput, uploadInput);
		uploadInput.parentNode.removeChild(uploadInput);
		uploadInput = newInput;
		_.bindEvent(uploadInput, 'change', onUploadChanged);
	};

	_.bindEvent(uploadContainer, 'click', function() {
		uploadInput.click();
	});

	_.bindEvent(uploadContainer, 'dragover', function(e) {
		e.stopPropagation();
		e.preventDefault();
		_.addClass(uploadContainer, 'dragover');
	});

	_.bindEvent(uploadContainer, 'dragleave', function(e) {
		e.stopPropagation();
		e.preventDefault();
		_.removeClass(uploadContainer, 'dragover');
	});

	_.bindEvent(uploadContainer, 'drop', function(e) {
		e.stopPropagation();
		e.preventDefault();
		var dt = e.dataTransfer;
		if (!dt) {
			return;
		}
		var files = dt.files;
		_.forEach(files, function(fileObject) {
			uploadFile(fileObject);
		});
		_.removeClass(uploadContainer, 'dragover');
	});

	_.bindEvent(uploadInput, 'change', onUploadChanged);

	var previews = [];

	var createPreview = function(data) {
		var element = attachmentTemplate.cloneNode(true);
		var img;

		_.removeClass(element, 'attachment-template');

		var thumbnailTemplate = _.cls(element, 'template-thumbnail')[0];
		if (thumbnailTemplate !== undefined) {
			var style = thumbnailTemplate.getAttribute('data-style');
			img = _.elem('IMG');
			if (style !== undefined) {
				img.setAttribute('style', style);
			}
			thumbnailTemplate.appendChild(img);
		}

		if (img !== undefined && data.thumbnails !== undefined && data.thumbnails.standard !== undefined) {
			img.setAttribute('src', data.thumbnails.standard);
			img.style.display = 'block';
		}
		else {
			img.style.display = 'none';
		}

		var urlTemplate = _.cls(element, 'template-url')[0];
		if (urlTemplate !== undefined) {
			if (data.url === undefined) {
				urlTemplate.appendChild(document.createTextNode(data.name));
			}
			else {
				urlTemplate.appendChild(_.elem('A', {'href': data.url}, data.name));
			}
		}

		var urlnameTemplate = _.cls(element, 'template-urlname')[0];
		if (urlnameTemplate !== undefined) {
			urlnameTemplate.appendChild(document.createTextNode(data.url || data.name));
		}

		var filesizeTemplate = _.cls(element, 'template-filesize')[0];
		if (filesizeTemplate !== undefined) {
			filesizeTemplate.appendChild(document.createTextNode(_.filesizeformat(data.filesize)));
		}

		var preview = {
			element: element,
			img: img,
			data: data
		};

		attachmentTemplate.parentNode.insertBefore(element, attachmentTemplate);
		previews.push(preview);
		return preview;
	};

	var updatePreviews = function() {
		var toDelete = [];
		_.forEach(previews, function(preview) {
			if (!preview.data.persistent) {
				toDelete.push(preview);
			}
		});
		previews = _.filter(previews, function(preview) {
			return preview.data.persistent;
		});
		_.forEach(toDelete, function(preview) {
			preview.element.parentNode.removeChild(preview.element);
		});

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

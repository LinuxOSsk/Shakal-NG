(function(_) {
"use strict";

var filesizeformat = function(bytes) {
	var KB = 1 << 10;
	var MB = 1 << 20;
	var GB = 1 << 30;
	var TB = 1 << 40;
	var PB = 1 << 50;

	var formatFloat = function(val) {
		return (Math.round(val * 100.0)) / 100.0;
	};

	if (bytes < KB) {
		return bytes + ' B';
	}
	else if (bytes < MB) {
		return formatFloat(bytes / KB) + ' KB';
	}
	else if (bytes < GB) {
		return formatFloat(bytes / MB) + ' MB';
	}
	else if (bytes < TB) {
		return formatFloat(bytes / GB) + ' GB';
	}
	else {
		return formatFloat(bytes / PB) + ' PB';
	}
};

window._utils.filesizeformat = filesizeformat;

var createUploader = function(element) {
	var uploadAjax = _.cls(element, 'attachment-upload-ajax')[0];
	if (uploadAjax === undefined) {
		return;
	}
	var form = element;
	while (form !== undefined && form.tagName != undefined && form.tagName.toLowerCase() !== 'form') {
		form = form.parentNode;
	}
	if (form === undefined || form.tagName === undefined) {
		return;
	}
	var uploadSession = _.id('id_upload_session').value;
	var attachmentTemplate = _.cls(uploadAjax, 'attachment-template')[0];
	var uploadContainer = _.cls(element, 'attachment-upload-container')[0];
	var uploadInput = _.cls(element, 'attachment-upload')[0];
	var attachedFiles = [];
	if (attachmentTemplate === undefined || uploadContainer === undefined || uploadInput === undefined) {
		return;
	}
	var attachmentTemplateSibling = attachmentTemplate.nextSibling;

	var submitButton;
	var submited = false;
	_.bindEvent(form, 'submit', function(event) {
		if (submited === false) {
			processNextFile();
			event.preventDefault();
		}
	});
	_.bindEvent(form, 'click', function(event) {
		var target = event.target;
		if (target.getAttribute('type') === 'submit') {
			if (submited === false) {
				submitButton = event.target;
				processNextFile();
				event.preventDefault();
			}
		}
	});

	_.addClass(element, 'ajax');
	uploadInput.style.visibility = 'hidden';
	uploadInput.style.display = 'block';
	uploadInput.style.width = '1px';
	uploadInput.style.height = '1px';
	uploadInput.style.position = 'absolute';

	var urls = {
		list: uploadAjax.getAttribute('data-list-url'),
		manage: uploadAjax.getAttribute('data-manage-url')
	};

	var uploading = false;
	var processNextFile = function() {
		if (uploading) {
			return;
		}
		uploading = true;

		var performUpload = function(attachment) {
			var formData = new FormData();
			formData.append('upload_session', uploadSession);
			formData.append('attachment_action', 'upload');
			formData.append('attachment', attachment.data.fileObject);

			var req = _.xhrSend({
				url: urls.manage,
				method: 'POST',
				data: formData,
				contentType: null,
				successFn: function(data, req) {
					attachment.data.persistent = false;
					attachment.data.fileObject = undefined;
					uploading = false;
					updatePreviewsFromData(data, req);
					processNextFile();
				},
				failFn: function() {
					attachment.data.persistent = false;
					attachment.data.fileObject = undefined;
					uploading = false;
					updatePreviews();
					processNextFile();
				},
				progress: function(e) {
					var percent = (e.loaded / e.total * 100);
					if (attachment.progress.value) {
						attachment.progress.value.style.width = percent + '%';
					}
				}
			});
		};

		var found = false;
		for (var i = 0, leni = attachedFiles.length; i < leni; i++) {
			var attachment = attachedFiles[i];
			if (attachment.data.fileObject !== undefined) {
				found = true;
				performUpload(attachment);
				break;
			}
		}

		if (!found) {
			uploading = false;
			if (submitButton === undefined) {
				submitButton = form.querySelector('[type="submit"]');
			}
			submited = true;
			submitButton.click();
		}
	};

	var enqueueFile = function(fileObject) {
		var mimetype = fileObject.type;
		var previewData = {
			name: fileObject.name,
			filesize: fileObject.size,
			persistent: true,
			fileObject: fileObject
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
		//processNextFile();
	};

	var onUploadChanged = function() {
		_.unbindEvent(uploadInput, 'change');
		_.forEach(uploadInput.files, function(fileObject) {
			enqueueFile(fileObject);
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
			enqueueFile(fileObject);
		});
		_.removeClass(uploadContainer, 'dragover');
	});

	_.bindEvent(uploadInput, 'change', onUploadChanged);

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
			filesizeTemplate.appendChild(document.createTextNode(filesizeformat(data.filesize)));
		}

		var progressTemplate = _.cls(element, 'template-progress')[0];
		var progressValue, progressContainer;
		if (data.persistent) {
			if (progressTemplate !== undefined) {
				progressContainer = _.elem('DIV', {'class': 'progress-container'});
				progressValue = _.elem('DIV', {'class': 'progress-value'});
				progressValue.style.width = '0%';
				progressContainer.appendChild(progressValue);
				progressTemplate.appendChild(progressContainer);
			}
		}

		var deleteTemplate = _.cls(element, 'template-delete')[0];
		if (deleteTemplate !== undefined) {
			deleteTemplate.onclick = function() {
				_.forEach(attachedFiles, function(preview, index) {
					if (preview.element !== element) {
						return;
					}
					element.parentNode.removeChild(element);
					attachedFiles.splice(index, 1);
					if (preview.data.id !== undefined) {
						var id = 0;
						while (document.getElementById('id_attachment-attachment-content_type-object_id-'+id+'-id') !== null) {
							var idInput = document.getElementById('id_attachment-attachment-content_type-object_id-'+id+'-id');
							if (idInput.value == preview.data.id) {
								document.getElementById('id_attachment-attachment-content_type-object_id-'+id+'-DELETE').checked = true;
							}
							id++;
						}
					}
				});
				return false;
			};
	}

		var preview = {
			element: element,
			img: img,
			data: data,
			progress: {
				value: progressValue,
				container: progressContainer
			}
		};

		if (data.persistent) {
			if (attachmentTemplateSibling) {
				attachmentTemplate.parentNode.insertBefore(element, attachmentTemplateSibling);
			}
			else {
				attachmentTemplate.parentNode.appendChild(element);
			}
		}
		else {
			attachmentTemplate.parentNode.insertBefore(element, attachmentTemplate);
		}
		attachedFiles.push(preview);
		return preview;
	};

	var updatePreviewsFromData = function(data, req) {
		if (req.isJSON !== true) {
			return;
		}
		if (data.upload_session) {
			uploadSession = data.upload_session;
			_.id('id_upload_session').value = uploadSession;
		}
		var toDelete = [];
		_.forEach(attachedFiles, function(preview) {
			if (!preview.data.persistent) {
				toDelete.push(preview);
			}
		});
		attachedFiles = _.filter(attachedFiles, function(preview) {
			return preview.data.persistent;
		});
		_.forEach(toDelete, function(preview) {
			preview.element.parentNode.removeChild(preview.element);
		});

		_.forEach(data.list, function(preview) {
			createPreview(preview);
		});
	};

	var updatePreviews = function() {
		var listUrl = urls.list;
		if (uploadSession) {
			listUrl += '&upload_session=' + encodeURIComponent(uploadSession);
		}
		_.xhrSend({
			url: listUrl,
			successFn: updatePreviewsFromData
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

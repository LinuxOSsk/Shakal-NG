(function (_) {

var SimpleEditorHtml = function(element, options) {
	var chrome = _.createDiv('richedit_chrome');
	var inner = _.createDiv('richedit_inner');
	var top = _.createDiv('richedit_top');
	var topOverlay = _.createDiv('richedit_top_overlay');
	var contents = _.createDiv('richedit_contents');
	var bottom = _.createDiv('richedit_bottom');
	var toolbox = _.createDiv('richedit_toolbox');
	var modal = _.createDiv('richedit_modal');
	var modalClose = document.createElement('A');
	var modalSubmit = document.createElement('A');
	var modalContent = _.createDiv('richedit_modal_content');

	modalClose.innerHTML = 'x';
	modalClose.className = 'richedit_modal_close';
	modalClose.setAttribute('href', '#');

	modalSubmit.innerHTML = 'VLOŽIŤ';
	modalSubmit.className = 'richedit_modal_submit';
	modalSubmit.setAttribute('href', '#');

	chrome.appendChild(inner);
	inner.appendChild(top);
	inner.appendChild(contents);
	inner.appendChild(bottom);
	top.appendChild(topOverlay);
	top.appendChild(toolbox);
	modal.appendChild(modalClose);
	modal.appendChild(modalSubmit);
	modal.appendChild(modalContent);
	contents.appendChild(modal);

	bottom.style.display = 'none';

	var addToolbar = function(group) {
		var toolbar = _.createDiv('richedit_toolbar');
		var toolbarStart = _.createDiv('richedit_toolbar_start');
		var toolbarGroup = _.createDiv(group === false ? undefined : 'richedit_toolgroup');
		var toolbarEnd = _.createDiv('richedit_toolbar_end');
		toolbar.appendChild(toolbarStart);
		toolbar.appendChild(toolbarGroup);
		toolbar.appendChild(toolbarEnd);
		toolbox.appendChild(toolbar);
		return toolbarGroup;
	};

	var addButton = function(group, options) {
		var down = false;
		var on = false;

		if (options.down) {
			down = true;
		}

		var className = 'richedit_button';
		if (options.cls !== undefined) {
			className += ' ' + options.cls;
		}

		var link = document.createElement('A');
		link.setAttribute('href', '#');

		if (options.title !== undefined) {
			link.setAttribute('title', options.title);
		}

		var btn = {options: options, link: link};

		var icon = document.createElement('SPAN');
		icon.className = 'richedit_button_icon';
		link.appendChild(icon);

		if (options.label !== undefined) {
			var label = document.createElement('SPAN');
			label.className = 'richedit_button_label';
			label.appendChild(document.createTextNode(options.label));
			link.appendChild(label);
		}

		if (options.cls === 'dropdown') {
			var arrow = document.createElement('SPAN');
			arrow.className = 'richedit_combo_open';
			arrow.innerHTML = '<span class="richedit_combo_arrow"></span>';
			link.appendChild(arrow);
		}

		var updateCls = function() {
			link.className = className + ' richedit_button_' + ((down || on) ? 'on': 'off');
		}
		updateCls();

		link.onmousedown = function(e) {
			if (down) {
				on = false;
				updateCls();
			}
			else {
				on = true;
				updateCls();
			}
			e.stopPropagation();
		};
		link.onmouseup = function(e) {
			on = false;
			if (options.toggle) {
				down = !down;
				if (options.ontoggle) {
					options.ontoggle(btn, down);
				}
			}
			else {
				if (options.onclick) {
					options.onclick(btn);
				}
			}
			updateCls();
			e.preventDefault();
			if (options.cls !== 'dropdown') {
				element.focus();
			}
		};
		link.onblur = function() {
			if (options.onblur) {
				options.onblur(btn);
			}
		};
		link.onmouseout = function() {
			on = false;
			updateCls();
		};
		link.onclick = function() {
			return false;
		};
		link.setDown = function(newDown) {
			down = newDown;
			updateCls();
		};

		group.appendChild(link);
		return link;
	};

	var addSeparator = function(group) {
		group.appendChild(_.createDiv('richedit_toolbar_separator'));
	};

	var addBreak = function(toolbar) {
		toolbar.appendChild(_.createDiv('richedit_toolbar_break'));
	};

	var addCombo = function(group) {
		var combo = document.createElement('SPAN');
		combo.className = 'richedit_combo';
		group.appendChild(combo);
		return combo;
	};

	var addComboMenu = function(group) {
		var comboMenu = document.createElement('UL');
		comboMenu.className = 'richedit_combo_menu';
		group.appendChild(comboMenu);
		return comboMenu;
	};

	var addComboMenuItem = function(menu, options) {
		var item = document.createElement('LI');
		var link = document.createElement('A');
		var btn = {options: options, link: link};
		if (options.cls !== undefined) {
			item.className = options.cls;
			link.className = 'richedit_combo_menu_link ' + options.cls;
		}
		else {
			link.className = 'richedit_combo_menu_link';
		}
		if (options.onclick !== undefined) {
			link.onmousedown = function() {
				options.onclick(btn);
			}
		}
		link.setAttribute('href', '#');
		link.appendChild(document.createTextNode(options.label));
		item.appendChild(link);
		menu.appendChild(item);
		return menu;
	};

	var triggerFunction = function(btn) {
		if (btn.options.parse) {
			var parseSel = btn.options.parse;
		}
		else {
			var parseSel = function(input) { return input; };
		}

		if (btn.options.tag_pre) {
			insert(btn.options.tag_pre, btn.options.tag_post, parseSel);
		}
		else {
			insert('<' + btn.options.tag + '>', '</' + btn.options.tag + '>', parseSel);
		}
	};

	var addModal = function(options) {
		chrome.className = 'richedit_chrome has_modal';
		modalContent.innerHTML = options.template;
		modalClose.onclick = function() {
			if (options.onClosed && options.onClosed()) {
				return;
			}
			removeModal();
			return false;
		}
		modalSubmit.onclick = function() {
			if (options.onSubmitted && options.onSubmitted()) {
				return;
			}
			removeModal();
			return false;
		}
	};

	var removeModal = function() {
		chrome.className = 'richedit_chrome';
		modalContent.innerHTML = '';
		modalClose.onclick = undefined;
		modalSubmit.onclick = undefined;
	};

	var addText = function(btn) {
		var options = {
			template: '\
				<h1>Vložiť text</h1>\
				<div class="form-row">\
					<label><input name="richedit_insert_text_type" type="radio" checked="checked" /> Odstavec</label>&nbsp;&nbsp;&nbsp;&nbsp;\
					<label><input name="richedit_insert_text_type" type="radio" /> Kód</label>\
				</div>\
				<div class="form-row"><textarea placeholder="Sem vložte text"></textarea></div>',
			onSubmitted: function() {
				var element = paragraphInput.checked ? 'p' : 'pre';
				var content = textInput.value;
				console.log(element, content);
			}
		};
		addModal(options);

		var paragraphInput = modalContent.getElementsByTagName('INPUT')[0];
		var textInput = modalContent.getElementsByTagName('TEXTAREA')[0];
	};

	var addLink = function(btn) {
	};

	var addTable = function(btn) {
	};

	var addImage = function(btn) {
	};

	var buttons = {};

	var tb = addToolbar();
	buttons.source = addButton(tb, {cls: 'icon-source', toggle: true, down: true});
	buttons.preview = addButton(tb, {cls: 'icon-preview', toggle: true});

	var tb = addToolbar();
	var blocks = addCombo(tb);
	buttons.style = addButton(tb, {
		label: 'Štýl',
		cls: 'dropdown',
		toggle: true,
		ontoggle: function(self, status) {
			if (status) {
				showMenu();
			}
			else {
				hideMenu();
			}
		}
	});

	var styleMenu = addComboMenu(tb);
	styleMenu.style.display = 'none';
	addComboMenuItem(styleMenu, {label: 'Nadpis 1', cls: 'h1', tag: 'h1', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Nadpis 2', cls: 'h2', tag: 'h2', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Nadpis 3', cls: 'h3', tag: 'h3', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Nadpis 4', cls: 'h4', tag: 'h4', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Nadpis 5', cls: 'h5', tag: 'h5', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Nadpis 6', cls: 'h6', tag: 'h6', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Odstavec', cls: 'p', tag: 'p', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Citácia', cls: 'blockquote', tag: 'blockquote', onclick: triggerFunction})
	addComboMenuItem(styleMenu, {label: 'Kód', cls: 'pre', tag: 'pre', onclick: triggerFunction})

	var showMenu = function() {
		if (styleMenu.style.display === 'block') {
			return;
		}
		styleMenu.style.display = 'block';
		_.bindEvent(document.body, 'mousedown', hideMenu);
	};

	var hideMenu = function() {
		if (styleMenu.style.display === 'none') {
			return;
		}
		styleMenu.style.display = 'none';
		buttons.style.setDown(false);
		_.unbindEvent(document.body, 'mousedown', hideMenu);
	};

	var insert = function(pre, post, parseSel) {
		var parseSel = parseSel || function(input) { return input; };
		element.focus();
		if (document.selection) {
			var sel = document.selection.createRange();
			sel.text = pre + parseSel(sel.text) + post;
			sel.moveEnd('character', -pre.length);
			sel.select();
		}
		else {
			if (element.selectionStart != undefined) {
				var start = element.selectionStart;
				var end = element.selectionEnd;
				var selection = element.value.substring(start,end);
				element.value = element.value.substring(0, start) + pre + parseSel(selection) + post + element.value.substring(end, element.value.length);
				element.setSelectionRange(start + pre.length, start + pre.length);
			}
			else {
				element.focus();
				element.value = element.value + pre + parseSel('') + post;
			}
		}
	};

	var formatListContent = function(input) {
		var rows = input.split('\n');
		var newRows = [];
		_.forEach(rows, function(row) {
			newRows.push('<li>' + row + '</li>\n');
		});
		return newRows.join('');
	};

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-bold', tag: 'strong', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-italic', tag: 'em', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-strike', tag: 'del', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-underline', tag: 'u', onclick: triggerFunction});
	addSeparator(tb);
	addButton(tb, {cls: 'icon-removeformat', tag: 'code', onclick: triggerFunction}); // code

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-superscript', tag: 'sup', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-subscript', tag: 'sub', onclick: triggerFunction});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-blockquote', tag: 'blockquote', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-pastetext', onclick: addText});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-bulletedlist', tag_pre: '<ul>\n', tag_post: '</ul>', parse: formatListContent, onclick: triggerFunction});
	addButton(tb, {cls: 'icon-numberedlist', tag_pre: '<ol>\n', tag_post: '</ol>', parse: formatListContent, onclick: triggerFunction});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-link', onclick: addLink});
	addButton(tb, {cls: 'icon-table', tag_pre: '<table>\n', tag_post: '</table>', row_pre: '<tr><td>', row_post: '</td><td></td><tr>\n', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-image', onclick: addImage});

	addBreak(top);
	addBreak(contents);
	addBreak(bottom);

	element.parentNode.insertBefore(chrome, element);
	contents.appendChild(element);

	this.destroy = function() {
		chrome.parentNode.insertBefore(element, chrome);
		chrome.parentNode.removeChild(chrome);
	};
};

var CkEditorHtml = function(element, options) {
	var self = this;
	var destroy = false;

	this.editor = undefined;

	var initializeEditor = function() {
		if (CKEDITOR._customized === undefined) {
			CKEDITOR._customized = true;

			CKEDITOR._extraCss = [CKEDITOR.getCss()];

			CKEDITOR.addCss = function(css) {
				CKEDITOR._extraCss.push(css);
			};

			CKEDITOR.getCss = function(css) {
				return CKEDITOR._extraCss.join('\n');
			};

			CKEDITOR.plugins.add('close', {
				init: function(editor) {
					editor.addCommand('close', {
						exec: function(self) {
							self._selector.selectEditor('simple_html');
						}
					});
					editor.ui.addButton('Close', {
						label: 'Prepnúť na obyčajný editor',
						command: 'close'
					});
				}
			});

			CKEDITOR.on('instanceReady', function() {
				_.forEach(_.cls(document.body, 'cke_button__close'), function(btn) {
					var toolbar = btn.parentNode.parentNode;
					toolbar.style.float = 'right';
					btn.parentNode.style.marginRight = '0';
				});
			});
		}

		var config = {};
		config.toolbar = [
			{ name: 'close', items: [ 'Close' ] },
			{ name: 'document', groups: [ 'mode', 'document', 'doctools' ], items: [ 'Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates' ] },
			{ name: 'clipboard', groups: [ 'clipboard', 'undo' ], items: [ 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo' ] },
			{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker' ], items: [ 'Find', 'Replace', '-', 'SelectAll', '-', 'Scayt' ] },
			{ name: 'forms', items: [ 'Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField' ] },
			{ name: 'styles', items: [ 'Styles', 'Format', 'Font', 'FontSize' ] },
			{ name: 'colors', items: [ 'TextColor', 'BGColor' ] },
			{ name: 'tools', items: [ 'Maximize', 'ShowBlocks' ] },
			{ name: 'others', items: [ '-' ] },
			{ name: 'about', items: [ 'About' ] },
			'/',
			{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat' ] },
			{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ], items: [ 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl', 'Language' ] },
			{ name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
			{ name: 'insert', items: [ 'Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe' ] },
		];
		config.plugins = 'basicstyles,blockquote,clipboard,contextmenu,dialogadvtab,enterkey,find,format,horizontalrule,image,indentblock,indentlist,justify,link,list,magicline,maximize,pastetext,removeformat,showblocks,showborders,sourcearea,specialchar,tab,table,tabletools,toolbar,undo,wysiwygarea,close';
		config.format_tags = 'p;h1;h2;h3;h4;h5;h6;pre';

		if (options.tags) {
			var allowedTags = '';
			var allowedTagsRestrict = '';
			_.forEach(options.tags.known, function(element) {
				if (element.length) {
					if (element === 'a') {
						allowedTagsRestrict += ';a[!href,rel]';
					}
					else if (element === 'img') {
						allowedTagsRestrict += ';img[!src]';
					}
					else {
						if (allowedTags.length > 0) {
							allowedTags += ' ';
						}
						allowedTags += element;
					}
				}
			});
			config.allowedContent = allowedTags + allowedTagsRestrict;
		}
		else {
			config.allowedContent = true;
			config.extraAllowedContent = 'dl dt dd';
		}
		config.startupOutlineBlocks = true;
		CKEDITOR.addCss(options.tags.unsupported.join(', ') + '{ background-color: #ff9999 !important; border: 1px solid red !important; }');
		self.editor = CKEDITOR.replace(element, config);
		self.editor._editorInstance = self;
		self.editor._selector = options.selector;
		CKEDITOR._extraCss.pop();
	};

	this.destroy = function() {
		destroy = true;
		if (self.editor !== undefined) {
			self.editor.destroy(false);
			self.editor = undefined;
		}
	};

	_.loaderJs([window._urls.static_base + 'vendor/ckeditor/ckeditor.js'], function() {
		if (destroy) {
			return;
		}
		initializeEditor();
	});
};

var RichEditor = function(element, options) {
	var self = this;
	var currentEditorWidget = undefined;

	var o = {};
	for (var k in options) { if (options.hasOwnProperty(k)) o[k] = options[k]; }

	var editors = {
		'simple_html': SimpleEditorHtml,
		'ckeditor_html': CkEditorHtml
	}

	this.selectEditor = function(name) {
		if (currentEditorWidget !== undefined) {
			currentEditorWidget.destroy();
			currentEditorWidget = undefined;
		}
		o.selector = self;
		currentEditorWidget = new editors[name](element, o);
		_.setCookie(o.namespace + '_richeditor', name, 3650);
	};

	var editor = _.getCookie(o.namespace + '_richeditor');
	if (editors[editor] === undefined) {
		editor = 'ckeditor_html';
	}
	this.selectEditor(editor);
};

_.RichEditor = RichEditor;

var rich_editors = window.rich_editors || [];
_.forEach(rich_editors, function(editorSettings) {
	new RichEditor(editorSettings.element, editorSettings);
});


}(window._utils));

(function (_) {

var SimpleEditorHtml = function(element, options) {
	var hasModal = false;
	var hasPreview = false;
	var hasCode = true;

	var chrome = _.createDiv('richedit_chrome');
	var inner = _.createDiv('richedit_inner');
	var top = _.createDiv('richedit_top');
	var topOverlay = _.createDiv('richedit_top_overlay');
	var contents = _.createDiv('richedit_contents');
	var contentsEdit = _.createDiv('richedit_contents_edit');
	var bottom = _.createDiv('richedit_bottom');
	var toolbox = _.createDiv('richedit_toolbox');
	var modal = _.createDiv('richedit_modal');
	var modalClose = document.createElement('A');
	var modalSubmit = document.createElement('A');
	var modalContent = _.createDiv('richedit_modal_content');
	var preview = document.createElement('IFRAME');
	preview.onload = function() { updatePreviewCss(); };
	preview.setAttribute('src', options.static_base + 'js/richeditor/iframe.html');

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
	contents.appendChild(preview);
	contents.appendChild(modal);
	contents.appendChild(contentsEdit);

	bottom.style.display = 'none';

	var updateChromeClass = function() {
		var cls = 'richedit_chrome';
		if (hasModal) {
			cls += ' has_modal';
		}
		if (hasPreview) {
			cls += ' has_preview';
		}
		if (hasCode) {
			cls += ' has_code';
		}
		chrome.className = cls;
	};

	var updatePreviewCss = function() {
		var doc = preview.documentElement ? preview.documentElement : (preview.contentDocument ? preview.contentDocument : preview.contentWindow.document)
		var inlineCss = doc.getElementsByTagName('STYLE')[0];
		inlineCss.innerHTML = options.tags.unsupported.join(', ') + '{ background-color: #ff9999 !important; border: 1px solid red !important; }';
	};

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
		if (options.onSubmitted === undefined) {
			modalSubmit.style.display = 'none';
		}
		else {
			modalSubmit.style.display = 'block';
		}
		hasModal = true;
		updateChromeClass();
		modalContent.innerHTML = options.template;
		modalContent.scrollTop = 0;
		modalClose.onclick = function(event) {
			if (options.onClosed && options.onClosed()) {
				return;
			}
			removeModal();
			return false;
		};
		modalSubmit.onclick = function(event) {
			if (options.onSubmitted && options.onSubmitted()) {
				return;
			}
			removeModal();
			return false;
		};
		modalContent.focus();
	};

	var removeModal = function() {
		if (hasModal) {
			hasModal = false;
			updateChromeClass();
			modalContent.innerHTML = '';
			modalClose.onclick = undefined;
			modalSubmit.onclick = undefined;
		}
	};

	var aboutEditor = function(btn) {
		var options = {
			template: '\
				<h1>O tomto editore</h1>\
				<p>Tento editor používa časti <a href="http://ckeditor.com/about/license">open source</a> editoru <a href="http://ckeditor.com/">CKEditor</a>.</p>\
				<h2>Klávesové skratky</h2>\
				<p><span class="richedit_key_shortcut">Shift + Enter</span> - nový riadok</p>\
				<p><span class="richedit_key_shortcut">Ctrl + Medzera</span> - nový odstavec</p>\
				<p><span class="richedit_key_shortcut">Ctrl + B</span> - tučné písmo</p>\
				<p><span class="richedit_key_shortcut">Ctrl + I</span> - šikmé písmo</p>\
				<p><span class="richedit_key_shortcut">Ctrl + C</span> - kód</p>\
				<p><span class="richedit_key_shortcut">Ctrl + Y</span> - riadok zoznamu</p>\
				<p><span class="richedit_key_shortcut">Ctrl + E</span> - prevod na HTML entity</p>\
				<h2>Tipy</h2>\
				<p>Výpisy alebo zdrojové kódy je možné do editoru vložiť priamo. Po vložeí stačí kód označiť a vybrať <span class="richedit_menu_help">Štýl</span> / <span class="richedit_menu_help">Kód</span>. Editor sa sám postará o ošetrenie znakov.</p>\
				<p>Text je možné transformovať na zoznam označením a kliknutím na ikonu zoznamu.</p>\
				<pre>          &lt;ul&gt;\nLinux       &lt;li&gt;Linux&lt;/li&gt;\nWindows     &lt;li&gt;Windows&lt;/li&gt;\nMac OS      &lt;li&gt;Mac OS&lt;/li&gt;\n          &lt;/ul&gt;</pre>\
				<p>Podobným spôsobom je možné transformovať tabuľku</p>\
				<pre>*Nadpis ; *Nadpis2\n Obsah  ;  Obsah ...\n\n&lt;table&gt;\n  &lt;tr&gt;\n    &lt;th&gt;Nadpis&lt;/th&gt;\n    &lt;th&gt;Nadpis2&lt;/th&gt;\n  &lt;/tr&gt;\n  &lt;tr&gt;\n    &lt;td&gt;Obsah&lt;/td&gt;\n    &lt;td&gt;Obsah ...&lt;/td&gt;\n  &lt;/tr&gt;\n&lt;/table&gt;</pre>\
			'
		};
		addModal(options);
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
				var tag = paragraphInput.checked ? 'p' : 'pre';
				var content = textInput.value;
				insert('<' + tag + '>' + _.escapeHTML(content) + '</' + tag + '>\n', '');
			}
		};
		addModal(options);

		var paragraphInput = modalContent.getElementsByTagName('INPUT')[0];
		var textInput = modalContent.getElementsByTagName('TEXTAREA')[0];
	};

	var addLink = function(btn) {
		var options = {
			template: '\
				<h1>Pridať odkaz</h1>\
				<div class="form-row horizontal">\
					<div class="formrow-label"><label>URL</label></div>\
					<div class="formrow-input"><input type="text" placeholder="http://www.adresa.sk/" /></div>\
				</div>\
				<div class="form-row horizontal">\
					<div class="formrow-label"><label>Text</label></div>\
					<div class="formrow-input"><input type="text" placeholder="Text odkazu" /></div>\
				</div>',
			onSubmitted: function() {
				var url = urlInput.value;
				var text = textInput.value;
				insert('<a href="' + _.escapeHTMLAttr(url) + '">' + text, '</a>');
			}
		};
		addModal(options);

		var inputs = modalContent.getElementsByTagName('INPUT');
		var urlInput = inputs[0];
		var textInput = inputs[1];
	};

	var addImage = function(btn) {
		var options = {
			template: '\
				<h1>Pridať obrázok</h1>\
				<div class="form-row horizontal">\
					<div class="formrow-label"><label>URL</label></div>\
					<div class="formrow-input"><input type="text" placeholder="http://www.adresa.sk/obrazok.png" /></div>\
				</div>\
				<div class="form-row horizontal">\
					<div class="formrow-label"><label>Alternatívny text</label></div>\
					<div class="formrow-input"><input type="text" placeholder="Alternatívny text napr. Tux" /></div>\
				</div>',
			onSubmitted: function() {
				var url = urlInput.value;
				var alt = altInput.value;
				insert('<img src="' + _.escapeHTMLAttr(url) + '" alt="' + _.escapeHTMLAttr(alt) + '"/>\n', '');
			}
		};
		addModal(options);

		var inputs = modalContent.getElementsByTagName('INPUT');
		var urlInput = inputs[0];
		var altInput = inputs[1];
	};

	var buttons = {};

	var tb = addToolbar();
	buttons.source = addButton(tb, {
		cls: 'icon-source',
		toggle: true,
		down: true,
		ontoggle: function(self, status) {
			hasCode = status;
			updateChromeClass();
		}
	});
	buttons.preview = addButton(tb, {
		cls: 'icon-preview',
		toggle: true,
		ontoggle: function(self, status) {
			hasPreview = status;
			updateChromeClass();
		}
	});

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
	addComboMenuItem(styleMenu, {label: 'Kód', cls: 'pre', tag: 'pre', onclick: triggerFunction, parse: _.escapeHTML})

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
			if (row[0] === '-' || row[0] === '*' || row[0] === '#') {
				row = row.substr(1);
				if (row[0] === ' ') {
					row = row.substr(1);
				}
			}
			newRows.push('<li>' + row + '</li>\n');
		});
		return newRows.join('');
	};

	var formatTableContent = function(input) {
		var rows = input.split('\n');
		var newRows = [];
		_.forEach(rows, function(row) {
			var columns = row.split(';');
			var newColumns = [];
			_.forEach(columns, function(column) {
				var column = column.trim();
				var tag = 'td';
				if (column[0] === '*') {
					tag = 'th';
					column = column.substr(1);
					if (column[0] === ' ') {
						column = column.substr(1);
					}
				}
				newColumns.push('    <' + tag + '>' + _.escapeHTML(column.trim()) + '</' + tag + '>\n');
			});
			newRows.push('  <tr>\n' + (newColumns.join('')) + '  </tr>\n');
		});
		return newRows.join('');
	};

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-bold', tag: 'strong', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-italic', tag: 'em', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-strike', tag: 'del', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-underline', tag: 'u', onclick: triggerFunction});
	addSeparator(tb);
	addButton(tb, {cls: 'icon-removeformat', tag: 'code', onclick: triggerFunction, parse: _.escapeHTML}); // code

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-superscript', tag: 'sup', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-subscript', tag: 'sub', onclick: triggerFunction});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-bidiltr', tag: 'p', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-blockquote', tag: 'blockquote', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-pastetext', onclick: addText});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-bulletedlist', tag_pre: '<ul>\n', tag_post: '</ul>', parse: formatListContent, onclick: triggerFunction});
	addButton(tb, {cls: 'icon-numberedlist', tag_pre: '<ol>\n', tag_post: '</ol>', parse: formatListContent, onclick: triggerFunction});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-link', onclick: addLink});
	addButton(tb, {cls: 'icon-table', tag_pre: '<table>\n', tag_post: '</table>', parse: formatTableContent, onclick: triggerFunction});
	addButton(tb, {cls: 'icon-image', onclick: addImage});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-about', onclick: aboutEditor});

	addBreak(top);
	addBreak(contents);
	addBreak(bottom);

	element.parentNode.insertBefore(chrome, element);
	contentsEdit.appendChild(element);

	element.onkeyup = function(event) {
		if (event.keyCode === 13) { // enter
			if (event.shiftKey) {
				insert('<br />\n', '');
				event.stopPropagation();
				return false;
			}
		}
		else if (event.keyCode === 32 && event.ctrlKey) { // ctrl + medzera
			insert('<p>', '</p>\n');
		}
		else if (event.keyCode === 66 && event.ctrlKey) { // ctrl + b
			insert('<strong>', '</strong>');
		}
		else if (event.keyCode === 73 && event.ctrlKey) { // ctrl + i
			insert('<em>', '</em>');
		}
		else if (event.keyCode === 67 && event.ctrlKey) { // ctrl + c
			insert('<code>', '</code>', _.escapeHTML);
		}
		else if (event.keyCode === 89 && event.ctrlKey) { // ctrl + y
			insert('<li>', '</li>');
		}
		else if (event.keyCode === 69 && event.ctrlKey) { // ctrl + e
			insert('', '', _.escapeHTML);
		}
		else if (event.keyCode === 112) { // help
			aboutEditor();
		}
	};
	element.onkeypress = function(event) {
		if (event.keyCode === 13) { // enter
			if (event.shiftKey) {
				return false;
			}
		}
	};

	var escModal = function(event) {
		if (event.keyCode === 27) {
			if (hasModal) {
				removeModal();
				element.focus();
			}
		}
	};

	_.bindEvent(document.body, 'keyup', escModal);

	var updateTimer = setInterval(function() {
		var text = element.value;
		preview.contentDocument.body.innerHTML = text;
	}, 1000);

	updateChromeClass();

	this.destroy = function() {
		clearInterval(updateTimer);
		chrome.parentNode.insertBefore(element, chrome);
		chrome.parentNode.removeChild(chrome);
		element.onkeyup = undefined;
		element.onkeypress = undefined;
		_.unbindEvent(document.body, 'keyup', escModal);
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
							self._switchContainer.style.display = 'block';
							self._selector.selectEditor('simple_html');
						}
					});
					editor.ui.addButton('Close', {
						label: 'Prepnúť na obyčajný editor',
						command: 'close'
					});
				}
			});

			CKEDITOR.on('instanceReady', function(self) {
				self.editor._switchContainer.style.display = 'none';
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
		self.editor._switchContainer = options.switchContainer;
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
	var currentEditor = undefined;

	var o = {};
	for (var k in options) { if (options.hasOwnProperty(k)) o[k] = options[k]; }

	var editors = {
		'simple_html': SimpleEditorHtml,
		'ckeditor_html': CkEditorHtml
	};

	var switchToolgroupContainer = _.createDiv('richedit_switch_toolgroup_container');
	var switchToolgroup = _.createDiv('richedit_toolgroup richedit_switch_toolgroup');
	var switchButton = document.createElement('A');
	switchButton.setAttribute('href', '#');
	switchButton.className = 'richedit_button';
	var label = document.createElement('SPAN');
	label.className = 'richedit_button_label';
	label.innerHTML = 'CKEditor';
	switchButton.appendChild(label);
	switchToolgroup.appendChild(switchButton);
	switchToolgroupContainer.appendChild(switchToolgroup);

	element.parentNode.insertBefore(switchToolgroupContainer, element);

	o.selector = self;
	o.switchContainer = switchToolgroupContainer;

	switchButton.onclick = function() {
		if (currentEditor === 'simple_html') {
			self.selectEditor('ckeditor_html');
		}
		else {
			self.selectEditor('simple_html');
		}
		return false;
	};

	this.selectEditor = function(name) {
		_.setCookie(o.namespace + '_richeditor', name, 3650);
		if (name === 'simple_html') {
			label.innerHTML = 'CKEditor';
		}
		else {
			label.innerHTML = 'Prepnúť na obyčajný editor';
		}

		currentEditor = name;
		try {
			if (currentEditorWidget !== undefined) {
				currentEditorWidget.destroy();
				currentEditorWidget = undefined;
			}
		}
		finally {
			currentEditorWidget = new editors[name](element, o);
		}
	};

	var editor = _.getCookie(o.namespace + '_richeditor');
	if (editors[editor] === undefined) {
		editor = 'simple_html';
	}
	this.selectEditor(editor);
};

_.RichEditor = RichEditor;

var rich_editors = window.rich_editors || [];
_.forEach(rich_editors, function(editorSettings) {
	new RichEditor(editorSettings.element, editorSettings);
});


}(window._utils));

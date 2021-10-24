(function (_) {

var E = _.el;

function escapeHTML(text) {
	return text
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;");
}

function escapeHTMLAttr(text) {
	return escapeHTML(text)
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

_.escapeHTML = escapeHTML;
_.escapeHTMLAttr = escapeHTMLAttr;


var SimpleEditorHtml = function(element, options) {
	function hasTag(tagName) {
		if (options.format === 'html') {
			if (options.tags.known.indexOf(tagName) !== -1) {
				return true;
			}
			else {
				return false;
			}
		}
		else {
			return true;
		}
	}

	var hasModal = false;
	var hasPreview = false;
	var hasCode = true;

	var chrome, inner, top, topOverlay, contents, contentsEdit, bottom, toolbox, modal, modalClose, modalSubmit, modalContent, preview;

	chrome = E('div.richedit_chrome',
		inner=E('div.richedit_inner',
			top=E('div.richedit_top',
				topOverlay=E('div.richedit_top_overlay'),
				toolbox=E('div.richedit_toolbox')
			),
			contents=E('div.richedit_contents',
				preview=E('iframe'),
				modal=E('div.richedit_modal',
					modalClose=E('a.richedit_modal_close', {'href': '#'}, 'x'),
					modalSubmit=E('a.richedit_modal_submit', {'href': '#'}, 'VLOŽIŤ'),
					modalContent=E('div.richedit_modal_content')
				),
				contentsEdit=E('div.richedit_contents_edit')
			),
			bottom=E('div.richedit_bottom')
		)
	);
	preview.onload = function() { updatePreviewCss(); };
	preview.setAttribute('src', options.static_base + 'js/richeditor/iframe.html');

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
		if (options.format !== 'html') {
			return;
		}
		var doc = preview.documentElement ? preview.documentElement : (preview.contentDocument ? preview.contentDocument : preview.contentWindow.document);
		var inlineCss = doc.getElementsByTagName('STYLE')[0];
		inlineCss.innerHTML = options.tags.unsupported.join(', ') + '{ background-color: #ff9999 !important; border: 1px solid red !important; }';
	};

	var parseYoutube = function(url) {
		var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
		var match = url.match(regExp);
		if (match && match[7].length == 11) {
			var videoId = match[7];
			return {
				id: videoId,
				canonical: 'https://www.youtube.com/watch?v=' + videoId,
				thumbnails: {
					'default': '//img.youtube.com/vi/' + videoId + '/default.jpg',
					'hqdefault': '//img.youtube.com/vi/' + videoId + '/hqdefault.jpg',
					'mqdefault': '//img.youtube.com/vi/' + videoId + '/qdefault.jpg'
				}
			};
		}
		else {
			return null;
		}
	};

	var addToolbar = function(group) {
		var toolbar, toolbarStart, toolbarEnd, toolbarGroup;
		toolbar = E('div.richedit_toolbar',
			toolbarStart=E('div.richedit_toolbar_start'),
			toolbarEnd=E('div.richedit_toolbar_end'),
			toolbarGroup=E('div')
		);
		if (group !== false) {
			toolbarGroup.className = 'richedit_toolgroup';
		}
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

		var link = E('a', {'href': '#'});

		if (options.title !== undefined) {
			link.setAttribute('title', options.title);
		}

		var btn = {options: options, link: link};

		var icon = E('span.richedit_button_icon');
		link.appendChild(icon);

		if (options.label !== undefined) {
			var label = E('span.richedit_button_label', options.label);
			link.appendChild(label);
		}

		if (options.cls === 'dropdown') {
			var arrow = E('span.richedit_combo_open', E('span.richedit_combo_arrow'));
			link.appendChild(arrow);
		}

		var updateCls = function() {
			link.className = className + ' richedit_button_' + ((down || on) ? 'on': 'off');
		};
		updateCls();

		_.bindEvent(link, 'mousedown', function() {
			if (down) {
				on = false;
				updateCls();
			}
			else {
				on = true;
				updateCls();
			}
		});
		link.onclick = function(e) {
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
			return false;
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
		link.setDown = function(newDown) {
			down = newDown;
			updateCls();
		};

		group.appendChild(link);
		return link;
	};

	var addSeparator = function(group) {
		group.appendChild(E('div.richedit_toolbar_separator'));
	};

	var addBreak = function(toolbar) {
		toolbar.appendChild(E('div.richedit_toolbar_break'));
	};

	var addCombo = function(group) {
		var combo = E('span.richedit_combo');
		group.appendChild(combo);
		return combo;
	};

	var addComboMenu = function(group) {
		var comboMenu = E('ul.richedit_combo_menu');
		group.appendChild(comboMenu);
		return comboMenu;
	};

	var addComboMenuItem = function(menu, options) {
		var link;
		var item = E('li', link=E('a', {'href': '#'}));
		var btn = {options: options, link: link};
		if (options.cls !== undefined) {
			item.className = options.cls;
			link.className = 'richedit_combo_menu_link ' + options.cls;
		}
		else {
			link.className = 'richedit_combo_menu_link';
		}
		if (options.onclick !== undefined) {
			_.bindEvent(link, 'click', function(e) {
				options.onclick(btn);
				hideMenuTrigger();
				e.preventDefault();
			});
		}
		link.appendChild(document.createTextNode(options.label));
		menu.appendChild(item);
		return menu;
	};

	var triggerFunction = function(btn) {
		var parseSel = btn.options.parse || function(input) { return input; };

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

		var closeModal = function(event) {
			if (options.onClosed && options.onClosed()) {
				return false;
			}
			removeModal();
			return false;
		};

		var submitModal = function(event) {
			if (options.onSubmitted && options.onSubmitted()) {
				return false;
			}
			removeModal();
			return false;
		};

		modalClose.onclick = closeModal;
		modalSubmit.onclick = submitModal;
		modalContent.focus();

		if (options.submitEnter) {
			modalContent.onkeyup = function(event) {
				if (event.keyCode === 13) { // enter
					event.stopPropagation();
					submitModal();
					return false;
				}
			};
			modalContent.onkeypress = function(event) {
				if (event.keyCode === 13) { // enter
					return false;
				}
			};
		}
		else {
			modalContent.onkeyup = null;
			modalContent.onkeypress = null;
		}
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
			template: ''+
				'<h1>O tomto editore</h1>'+
				'<p>Tento editor používa časti <a href="http://ckeditor.com/about/license">open source</a> editoru <a href="http://ckeditor.com/">CKEditor</a>.</p>'+
				'<h2>Klávesové skratky</h2>'+
				'<p><span class="richedit_key_shortcut">Shift + Enter</span> - nový riadok</p>'+
				'<p><span class="richedit_key_shortcut">Ctrl + Medzera</span> - nový odstavec</p>'+
				'<p><span class="richedit_key_shortcut">Ctrl + B</span> - tučné písmo</p>'+
				'<p><span class="richedit_key_shortcut">Ctrl + I</span> - šikmé písmo</p>'+
				'<p><span class="richedit_key_shortcut">Ctrl + Y</span> - riadok zoznamu</p>'+
				'<p><span class="richedit_key_shortcut">Ctrl + E</span> - prevod na HTML entity</p>'+
				'<h2>Tipy</h2>'+
				'<p>Výpisy alebo zdrojové kódy je možné do editoru vložiť priamo. Po vložeí stačí kód označiť a vybrať <span class="richedit_menu_help">Štýl</span> / <span class="richedit_menu_help">Kód</span>. Editor sa sám postará o ošetrenie znakov.</p>'+
				'<p>Text je možné transformovať na zoznam označením a kliknutím na ikonu zoznamu.</p>'+
				'<pre>          &lt;ul&gt;\nLinux       &lt;li&gt;Linux&lt;/li&gt;\nWindows     &lt;li&gt;Windows&lt;/li&gt;\nMac OS      &lt;li&gt;Mac OS&lt;/li&gt;\n          &lt;/ul&gt;</pre>'+
				'<p>Podobným spôsobom je možné transformovať tabuľku</p>'+
				'<pre>*Nadpis ; *Nadpis2\n Obsah  ;  Obsah ...\n\n&lt;table&gt;\n  &lt;tr&gt;\n    &lt;th&gt;Nadpis&lt;/th&gt;\n    &lt;th&gt;Nadpis2&lt;/th&gt;\n  &lt;/tr&gt;\n  &lt;tr&gt;\n    &lt;td&gt;Obsah&lt;/td&gt;\n    &lt;td&gt;Obsah ...&lt;/td&gt;\n  &lt;/tr&gt;\n&lt;/table&gt;</pre>'
		};
		addModal(options);
	};

	var addText = function(btn) {
		var inputs = [];
		var lexersCode = '';
		var checked = true;
		if (hasTag('p') && btn.options.tag !== 'pre') {
			inputs.push('<label><input name="richedit_insert_text_type" type="radio"' + (checked ? 'checked="checked"' : '') + ' value="p" /> Odstavec</label>&nbsp;&nbsp;&nbsp;&nbsp;');
			checked = false;
		}
		if (hasTag('pre')) {
			if (btn.options.tag !== 'pre') {
				inputs.push('<label><input name="richedit_insert_text_type" type="radio"' + (checked ? 'checked="checked"' : '') + ' value="pre" /> Kód</label>&nbsp;&nbsp;&nbsp;&nbsp;');
			}
			checked = false;
			var optionElements = [];
			optionElements.push('<option value="">Vyberte zvýrazňovanie</option>');
			options.lexers.forEach(function(lexer) {
				optionElements.push('<option value="' + lexer[0] + '">' + _.escapeHTML(lexer[1]) + '</option>');
			});
			lexersCode = '<div class="form-row"><label>Zvýrazniť kód: <select>' + (optionElements.join('')) + '<select></label></div>';
		}

		var modalOptions = {
			template: ''+
				'<h1>Vložiť text</h1>' +
				'<div class="form-row">' + (inputs.join('')) + '</div>' + lexersCode +
				'<div class="form-row"><textarea placeholder="Sem vložte text"></textarea></div>',
			onSubmitted: function() {
				var content = textInput.value;
				if (tag !== undefined) {
					var highlight = '';
					if (tag === 'pre' && highlightSelect !== undefined && highlightSelect.value !== '') {
						highlight = ' class="code-' + highlightSelect.value + '"';
					}
					insert('<' + tag + highlight + '>' + _.escapeHTML(content) + '</' + tag + '>\n', '');
				}
				else {
					insert(_.escapeHTML(content) + '\n', '');
				}
			}
		};
		addModal(modalOptions);

		var inputElements = _.qa('input', modalContent);
		var textInput = _.q('textarea', modalContent);
		var highlightSelect = _.q('select', modalContent);
		var tag;

		var selectTag = function() {
			tag = btn.options.tag;
			inputElements.forEach(function(input) {
				if (input.checked) {
					tag = input.value;
				}
			});
			if (tag === 'pre' && highlightSelect !== undefined) {
				highlightSelect.parentNode.parentNode.style.display = 'block';
			}
			else {
				if (highlightSelect !== undefined) {
					highlightSelect.parentNode.parentNode.style.display = 'none';
				}
			}
		};

		inputElements.forEach(function(input) {
			input.onchange = selectTag;
		});

		selectTag();
	};


	var addLink = function(btn) {
		var options = {
			template: ''+
				'<h1>Pridať odkaz</h1>'+
				'<div class="form-row horizontal">'+
					'<div class="formrow-label"><label>URL</label></div>'+
					'<div class="formrow-input"><input type="text" placeholder="http://www.adresa.sk/" /></div>'+
				'</div>'+
				'<div class="form-row horizontal">'+
					'<div class="formrow-label"><label>Text</label></div>'+
					'<div class="formrow-input"><input type="text" placeholder="Text odkazu" /></div>'+
				'</div>',
			submitEnter: true,
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
			template: ''+
				'<h1>Pridať obrázok</h1>'+
				'<div class="form-row horizontal">'+
					'<div class="formrow-label"><label>URL</label></div>'+
					'<div class="formrow-input"><input type="text" placeholder="http://www.adresa.sk/obrazok.png" /></div>'+
				'</div>'+
				'<div class="form-row horizontal">'+
					'<div class="formrow-label"><label>Alternatívny text</label></div>'+
					'<div class="formrow-input"><input type="text" placeholder="Alternatívny text napr. Tux" /></div>'+
				'</div>',
			submitEnter: true,
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

	var addVideo = function(btn) {
		var options = {
			template: ''+
				'<h1>Pridať youtube video</h1>'+
				'<div class="form-row horizontal">'+
					'<div class="formrow-label"><label>URL</label></div>'+
					'<div class="formrow-input"><input type="text" placeholder="https://www.youtube.com/watch?v=xxxxxxxxxxx" /></div>'+
				'</div>',
			submitEnter: true,
			onSubmitted: function() {
				var url = urlInput.value;
				var youtube = parseYoutube(url);
				if (youtube !== null) {
					insert('<a href="' + _.escapeHTMLAttr(youtube.canonical) + '"><img src="' + _.escapeHTMLAttr(youtube.thumbnails.hqdefault) + '" alt="Video"/></a>', '');
				}
				else {
					return true;
				}
			}
		};
		addModal(options);

		var inputs = modalContent.getElementsByTagName('INPUT');
		var urlInput = inputs[0];
	};

	var insert = function(pre, post, parseSelFilter) {
		var parseSel = parseSelFilter || function(input) { return input; };
		element.focus();
		if (document.selection) {
			var sel = document.selection.createRange();
			sel.text = pre + parseSel(sel.text) + post;
			sel.moveEnd('character', -pre.length);
			sel.select();
		}
		else {
			if (element.selectionStart !== undefined) {
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
		rows.forEach(function(row) {
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
		rows.forEach(function(row) {
			var columns = row.split(';');
			var newColumns = [];
			columns.forEach(function(col) {
				var column = col.trim();
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

	var buttons = {};

	var updatePreview = function() {
		var text = element.value;
		preview.contentDocument.body.innerHTML = text;
		var format = options.format;
		var parser = options.parsers[format];
		_.xhrSend({
			method: 'POST',
			url: options.preview,
			data: 'format=' + encodeURIComponent(format) + '&parser=' + encodeURIComponent(parser) + '&text=' + encodeURIComponent(text),
			successFn: function(response) {
				preview.contentDocument.body.innerHTML = response;
			}
		});
	};

	var tb;
	tb = addToolbar();
	buttons.source = addButton(tb, {
		cls: 'icon-source',
		title: 'Zdrojový kód',
		toggle: true,
		down: true,
		ontoggle: function(self, status) {
			hasCode = status;
			hasPreview = !status;
			buttons.preview.setDown(hasPreview);
			updateChromeClass();
			if (hasPreview) {
				updatePreview();
			}
		}
	});
	buttons.preview = addButton(tb, {
		cls: 'icon-preview',
		title: 'Náhľad',
		toggle: true,
		ontoggle: function(self, status) {
			hasPreview = status;
			hasCode = !status;
			buttons.source.setDown(hasCode);
			updateChromeClass();
			if (hasPreview) {
				updatePreview();
			}
		}
	});

	if (hasTag('h1') || hasTag('h2') || hasTag('h3') || hasTag('h4') || hasTag('h5') || hasTag('h6') || hasTag('p') || hasTag('blockquote') || hasTag('pre')) {
		tb = addToolbar();
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
		if (hasTag('h1')) addComboMenuItem(styleMenu, {label: 'Nadpis 1', cls: 'h1', tag: 'h1', onclick: triggerFunction});
		if (hasTag('h2')) addComboMenuItem(styleMenu, {label: 'Nadpis 2', cls: 'h2', tag: 'h2', onclick: triggerFunction});
		if (hasTag('h3')) addComboMenuItem(styleMenu, {label: 'Nadpis 3', cls: 'h3', tag: 'h3', onclick: triggerFunction});
		if (hasTag('h4')) addComboMenuItem(styleMenu, {label: 'Nadpis 4', cls: 'h4', tag: 'h4', onclick: triggerFunction});
		if (hasTag('h5')) addComboMenuItem(styleMenu, {label: 'Nadpis 5', cls: 'h5', tag: 'h5', onclick: triggerFunction});
		if (hasTag('h6')) addComboMenuItem(styleMenu, {label: 'Nadpis 6', cls: 'h6', tag: 'h6', onclick: triggerFunction});
		if (hasTag('p')) addComboMenuItem(styleMenu, {label: 'Odstavec', cls: 'p', tag: 'p', onclick: triggerFunction});
		if (hasTag('blockquote')) addComboMenuItem(styleMenu, {label: 'Citácia', cls: 'blockquote', tag: 'blockquote', onclick: triggerFunction});
		if (hasTag('pre')) addComboMenuItem(styleMenu, {label: 'Kód', cls: 'pre', tag: 'pre', onclick: triggerFunction, parse: _.escapeHTML});

		var hideMenuTrigger = function() {
			setTimeout(hideMenu, 0);
		};

		var showMenu = function() {
			if (styleMenu.style.display === 'block') {
				return;
			}
			styleMenu.style.display = 'block';
			_.bindEvent(document.body, 'mouseup', hideMenuTrigger);
		};

		var hideMenu = function() {
			if (styleMenu.style.display === 'none') {
				return;
			}
			styleMenu.style.display = 'none';
			buttons.style.setDown(false);
			_.unbindEvent(document.body, 'mouseup', hideMenuTrigger);
		};
	}

	if (hasTag('strong') || hasTag('em') || hasTag('del') || hasTag('u') || hasTag('code')) {
		tb = addToolbar();
		if (hasTag('strong')) addButton(tb, {cls: 'icon-bold', tag: 'strong', title: 'Tučné', onclick: triggerFunction});
		if (hasTag('em')) addButton(tb, {cls: 'icon-italic', tag: 'em', title: 'Kurzíva', onclick: triggerFunction});
		if (hasTag('del')) addButton(tb, {cls: 'icon-strike', tag: 'del', title: 'Preškrtnuté', onclick: triggerFunction});
		if (hasTag('u')) addButton(tb, {cls: 'icon-underline', tag: 'u', title: 'Podčiarknuté', onclick: triggerFunction});
		if (hasTag('code')) {
			addSeparator(tb);
			addButton(tb, {cls: 'icon-removeformat', tag: 'code', title: 'Inline kód', onclick: triggerFunction, parse: _.escapeHTML}); // code
		}
	}

	/*
	if (hasTag('sup') || hasTag('sub')) {
		tb = addToolbar();
		if (hasTag('sup')) addButton(tb, {cls: 'icon-superscript', tag: 'sup', title: 'Horný index', onclick: triggerFunction});
		if (hasTag('sup')) addButton(tb, {cls: 'icon-subscript', tag: 'sub', title: 'Dolný index', onclick: triggerFunction});
	}
	*/

	tb = addToolbar();
	if (hasTag('p')) addButton(tb, {cls: 'icon-bidiltr', tag: 'p', title: 'Odstavec', onclick: triggerFunction});
	if (hasTag('blockquote')) addButton(tb, {cls: 'icon-blockquote', tag: 'blockquote', title: 'Citácia', onclick: triggerFunction});
	if (hasTag('pre')) addButton(tb, {cls: 'icon-code', tag: 'pre', title: 'Kód', onclick: addText});
	if (hasTag('p') || hasTag('pre')) addButton(tb, {cls: 'icon-pastetext', title: 'Vložiť text, alebo zdrojový kód', onclick: addText});

	if (hasTag('ul') || hasTag('ol')) {
		tb = addToolbar();
		if (hasTag('ul')) addButton(tb, {cls: 'icon-bulletedlist', tag_pre: '<ul>\n', tag_post: '</ul>', title: 'Zoznam', parse: formatListContent, onclick: triggerFunction});
		if (hasTag('ol')) addButton(tb, {cls: 'icon-numberedlist', tag_pre: '<ol>\n', tag_post: '</ol>', title: 'Číslovaný zoznam', parse: formatListContent, onclick: triggerFunction});
	}

	if (hasTag('a') || hasTag('table') || hasTag('img')) {
		tb = addToolbar();
		if (hasTag('a')) addButton(tb, {cls: 'icon-link', title: 'Odkaz', onclick: addLink});
		if (hasTag('table')) addButton(tb, {cls: 'icon-table', tag_pre: '<table>\n', tag_post: '</table>', title: 'Tabuľka', parse: formatTableContent, onclick: triggerFunction});
		if (hasTag('img')) addButton(tb, {cls: 'icon-image', title: 'Obrázok', onclick: addImage});
	}

	if (hasTag('a') && hasTag('img')) {
		addButton(tb, {cls: 'icon-flash', title: 'Video', onclick: addVideo});
	}

	tb = addToolbar();
	addButton(tb, {cls: 'icon-about', title: 'Pomoc', onclick: aboutEditor});

	addBreak(top);
	addBreak(contents);
	addBreak(bottom);

	element.parentNode.insertBefore(chrome, element);
	contentsEdit.appendChild(element);

	element.onkeyup = function(event) {
		if (event.keyCode === 13) { // enter
			if (event.shiftKey) {
				insert('<br />', '');
				event.stopPropagation();
				return false;
			}
		}
		else if (event.keyCode === 32 && event.ctrlKey) { // ctrl + medzera
			insert('<p>', '</p>');
		}
		else if (event.keyCode === 66 && event.ctrlKey) { // ctrl + b
			insert('<strong>', '</strong>');
		}
		else if (event.keyCode === 73 && event.ctrlKey) { // ctrl + i
			insert('<em>', '</em>');
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

	updateChromeClass();

	this.destroy = function() {
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
							self._selector.selectEditor('default');
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
				_.qa('.cke_button__close').forEach(function(btn) {
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

		if (options.format === 'html' && options.tags) {
			var allowedTags = '';
			var allowedTagsRestrict = '';
			options.tags.known.forEach(function(element) {
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

	_.loaderJs([options.static_base + 'vendor/ckeditor/ckeditor.js'], function() {
		if (destroy) {
			return;
		}
		initializeEditor();
	});
};

var RichEditor = function(element, options) {
	var self = this;
	var currentEditorWidget;
	var currentEditor;
	var formats = _.q('.formatwrapper', element.parentNode);
	var format = '';

	if (formats !== null) {
		formats = _.qa('input', formats);
	}

	var getFormat = function() {
		var format = 'html';
		if (formats !== undefined) {
			formats.forEach(function(formatInput) {
				if (formatInput.checked) {
					format = formatInput.value;
				}
			});
		}
		return format;
	};

	var onChangeFormat = function() {
		var newFormat = getFormat();
		if (format !== newFormat) {
			format = newFormat;
			initializeEditor();
		}
	};

	if (formats !== null) {
		formats.forEach(function(formatInput) {
			formatInput.onchange = onChangeFormat;
		});
	}

	var editors = {
		'html': {
			'default': SimpleEditorHtml,
			'ckeditor_html': CkEditorHtml
		},
		'raw': {
			'default': SimpleEditorHtml,
			'ckeditor_html': CkEditorHtml
		}
	};

	var switchToolgroupContainer;

	var richeditContainer = E('div.richedit_container');
	element.parentNode.insertBefore(richeditContainer, element);
	element.parentNode.removeChild(element);
	richeditContainer.appendChild(element);

	var initializeEditor = function() {
		if (switchToolgroupContainer !== undefined) {
			switchToolgroupContainer.parentNode.removeChild(switchToolgroupContainer);
			switchToolgroupContainer = undefined;
		}
		if (currentEditorWidget !== undefined) {
			currentEditorWidget.destroy();
			currentEditorWidget = undefined;
		}

		var o = {};
		for (var k in options) { if (options.hasOwnProperty(k)) o[k] = options[k]; }
		o.format = format;

		var switchToolgroup, switchButton, lable;
		switchToolgroupContainer = E('div.richedit_switch_toolgroup_container',
			switchToolgroup=E('div.richedit_toolgroup.richedit_switch_toolgroup',
				switchButton=E('a.richedit_button', {'href': '#'},
					label=E('span.richedit_button_label', 'CKEditor')
				)
			)
		);
		richeditContainer.insertBefore(switchToolgroupContainer, element);

		o.selector = self;
		o.switchContainer = switchToolgroupContainer;

		switchButton.onclick = function() {
			if (currentEditor === 'default') {
				self.selectEditor('ckeditor_html');
			}
			else {
				self.selectEditor('default');
			}
			return false;
		};

		self.selectEditor = function(name) {
			_.setCookie(o.namespace + '_' + format + '_richeditor', name, 3650);
			if (name === 'default') {
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
				currentEditorWidget = new editors[format][name](element, o);
			}
		};

		var editor = _.getCookie(o.namespace + '_' + format + '_richeditor');
		if (editors[format][editor] === undefined) {
			editor = 'default';
		}
		self.selectEditor(editor);
	};

	onChangeFormat();
};

_.RichEditor = RichEditor;

var rich_editors = window.rich_editors || [];
rich_editors.forEach(function(editorSettings) { new RichEditor(editorSettings.element, editorSettings); });


}(window._utils2));

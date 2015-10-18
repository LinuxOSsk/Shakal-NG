/*
var all_tools = [
	{name:"Undo",title:"Undo",css:"wym_tools_undo"},
	{name:"Redo",title:"Redo",css:"wym_tools_redo"},
	{name:"Bold",title:"Strong",css:"wym_tools_strong",tag:"strong"},
	{name:"Italic",title:"Emphasis",css:"wym_tools_emphasis",tag:"em"},
	//{name:"Superscript",title:"Superscript",css:"wym_tools_superscript",tag:"sup"},
	//{name:"Subscript",title:"Subscript",css:"wym_tools_subscript",tag:"sub"},
	{name:"InsertOrderedList",title:"Ordered_List",css:"wym_tools_ordered_list",tag:"ol"},
	{name:"InsertUnorderedList",title:"Unordered_List",css:"wym_tools_unordered_list",tag:"ul"},
	{name:"Indent",title:"Indent",css:"wym_tools_indent"},
	{name:"Outdent",title:"Outdent",css:"wym_tools_outdent"},
	{name:"CreateLink",title:"Link",css:"wym_tools_link",tag:"a",tag_pre:'<a href="">',tag_post:"</a>"},
	{name:"Unlink",title:"Unlink",css:"wym_tools_unlink"},
	{name:"InsertImage",title:"Image",css:"wym_tools_image",tag:"img"},
	//{name:"InsertTable",title:"Table",css:"wym_tools_table",tag:"table"},
	{name:"Paste",title:"Paste_From_Word",css:"wym_tools_paste"},
	{name:"ToggleHtml",title:"HTML",css:"wym_tools_html"},
	{name:"Preview",title:"Preview",css:"wym_tools_preview"}
];
var all_containers = [
	{name:"P",title:"Paragraph",css:"wym_containers_p",tag:"p"},
	{name:"H1",title:"Heading_1",css:"wym_containers_h1",tag:"h1"},
	{name:"H2",title:"Heading_2",css:"wym_containers_h2",tag:"h2"},
	{name:"H3",title:"Heading_3",css:"wym_containers_h3",tag:"h3"},
	{name:"H4",title:"Heading_4",css:"wym_containers_h4",tag:"h4"},
	{name:"H5",title:"Heading_5",css:"wym_containers_h5",tag:"h5"},
	{name:"H6",title:"Heading_6",css:"wym_containers_h6",tag:"h6"},
	{name:"PRE",title:"Preformatted",css:"wym_containers_pre",tag:"pre"},
	{name:"BLOCKQUOTE",title:"Blockquote","css": "wym_containers_blockquote",tag:"blockquote"},
	{name:"TH",title:"Table_Header",css:"wym_containers_th",tag:"th"}
];

function filterTools(tools, selectors) {
	var ret_tools = [];
	for (var i = 0; i < tools.length; ++i) {
		if (tools[i].tag == undefined || selectors.indexOf(tools[i].tag) != -1) {
			ret_tools.push(tools[i]);
		}
	}
	return ret_tools;
}

var generate_unsupported_tags = function(frame, unsupported_tags) {
	var doc = frame.contentDocument;
	var styleEl = doc.createElement('style');
	styleEl.type = 'text/css';
	var style = doc.createTextNode(unsupported_tags.join(', ') + '{ background-color: #ff9999 !important; border: 1px solid red !important; }');
	styleEl.appendChild(style);
	var link = doc.getElementsByTagName('link')[0];
	link.parentNode.appendChild(styleEl);
};

var wymeditor_plugin = function(element, settings) {
	var editor = undefined;
	var resizeTimer = undefined;

	this.load = function()
	{
		loader([settings.static_base + 'js/jquery-1.8.3.min.js', settings.static_base + 'js/jquery-migrate-1.2.1.js'], function() {
			loader([settings['script_wymeditor']], function() {
				loader([settings.static_base + 'js/wymeditor/skins/shakal/skin.js'], function() {
					var tools = all_tools;
					var containers = all_tools;
					if (settings.tags != undefined) {
						tools = filterTools(all_tools, settings.tags.known);
						containers = filterTools(all_containers, settings.tags.known);
					}
					var options = {
							skin: settings.skin,
							lang: settings['lang'],
							statusHtml: '',
							updateSelector: jQuery(element).parents('form:first'),
							updateEvent: 'submit',
							basePath: settings.static_base + '/js/wymeditor/',
							postInit: function(wym) {
								editor = wym;
								$(wym._iframe.contentWindow.document.body).css({'overflow-y': 'hidden'});
								resizeTimer = setInterval(function() {
									$(wym._iframe).css('height', Math.max(206, wym._iframe.contentWindow.document.body.offsetHeight + 35) + 'px');
								}, 500);
								//wym.table();
							},
							toolsItems: tools,
							containersItems: containers
						};
					if (settings.skin == 'shakal') {
						options['toolsItemHtml'] = String() +
								'<li class="' + WYMeditor.TOOL_CLASS + ' btn" onclick="this.childNodes[0].childNodes[0].click()">' +
									'<span>' +
										'<a href="#" name="' + WYMeditor.TOOL_NAME + '" ' +
											'title="' + WYMeditor.TOOL_TITLE + '">' +
											WYMeditor.TOOL_TITLE +
										'</a>' +
									'</span>' +
								'</li>';
					}
					jQuery(element).wymeditor(options);
					var iframe = element.parentNode.getElementsByTagName('iframe')[0];
					var old_onload = iframe.onload;
					iframe.onload = function(event) {
						this.onload = old_onload;
						if (settings.tags != undefined) {
							generate_unsupported_tags(iframe, settings.tags.unsupported);
						}
					};
					settings.onLoad();
				});
			});
		});
	};

	this.unload = function()
	{
		if (editor != undefined) {
			editor.update();
		}
		element.style.display = 'block';
		var editor_div = element.parentNode.getElementsByTagName('div')[1];
		editor_div.parentNode.removeChild(editor_div);
		if (resizeTimer != undefined) {
			clearInterval(resizeTimer);
			resizeTimer = undefined;
		}
	};
};


var shakal_plugin = function(element, settings)
{
	var wymbox = undefined;

	this.insert = function(pre, post)
	{
		element.focus();
		if (document.selection) {
			var sel = document.selection.createRange();
			sel.text = pre + sel.text + post;
			sel.moveEnd('character', -pre.length);
			sel.select();
		}
		else {
			if (element.selectionStart != undefined) {
				var start = element.selectionStart;
				var end = element.selectionEnd;
				var selection = element.value.substring(start,end);
				element.value = element.value.substring(0, start) + pre + selection + post + element.value.substring(end, element.value.length);
				element.setSelectionRange(start + pre.length, start + pre.length);
			}
			else {
				element.focus();
				element.value = element.value + pre + post;
			}
		}
	}

	this.load = function() {
		wymbox = document.createElement("div");
		wymbox.className = "wym_box wym_box_0 wym_skin_shakal";

		var wymtop = document.createElement("div");
		wymtop.className = "wym_area_top";

		var wymcontainers = document.createElement("div");
		wymcontainers.className = "wym_containers wym_section wym_panel";

		var wymtools = document.createElement("div");
		wymtools.className = "wym_tools wym_section wym_buttons";

		wymtop.appendChild(wymcontainers);
		wymtop.appendChild(wymtools);
		wymbox.appendChild(wymtop);
		element.parentNode.insertBefore(wymbox, element);

		var tools = all_tools;
		var containers = all_containers;
		if (settings.tags != undefined) {
			tools = filterTools(all_tools, settings.tags.known);
			containers = filterTools(all_containers, settings.tags.known);
		}
		var insert = this.insert;

		var xmlhttp;
		if (window.XMLHttpRequest) {
			xmlhttp = new XMLHttpRequest();
		}
		else {
			xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
		}

		xmlhttp.open('GET', settings.static_base + '/js/wymeditor/lang/sk.js', true);
		xmlhttp.onload = function() {
			if (xmlhttp.status == 200) {
				var response = xmlhttp.responseText;
				response = response.substr(response.indexOf('{') - 1);
				response = response.substr(0, response.lastIndexOf(';'));
				var trans = eval("("+response+")");

				var createToolElement = function(item, extra_css) {
					var btn = document.createElement("li");
					btn.className = item.css + " " + extra_css;
					btn.onclick = function() { this.childNodes[0].childNodes[0].click(); };

					var span = document.createElement("span");

					var link = document.createElement("a");
					link.name = item.name;
					link.href = '#';
					link.innerHTML = trans[item.title];
					link.onclick = function(item) {
						return function(event) {
							event.stopPropagation();
							if (window.event != undefined) {
								window.event.cancelBubble = true;
							}
							if (item.tag_pre) {
								insert(item.tag_pre, item.tag_post);
							}
							else {
								insert('<' + item.tag + '>', '</' + item.tag + '>');
							}
							return false;
						}
					}(item);

					span.appendChild(link);
					btn.appendChild(span);
					return btn;
				}

				var wymcontainers_btn = document.createElement("div");
				wymcontainers_btn.className = "btn";
				var wymcontainers_inner = document.createElement("span");
				wymcontainers_btn.appendChild(wymcontainers_inner);
				wymcontainers_inner.innerHTML = '<span class="dropdown">'+trans.Containers+'<span class="icon"></span></span>';
				wymcontainers.appendChild(wymcontainers_btn);

				var wym_top_toolbar = document.createElement("div");
				wym_top_toolbar.className = "wym_top_toolbar";
				wymcontainers.appendChild(wym_top_toolbar);
				var wymcontainers_list = document.createElement("ul");
				wym_top_toolbar.appendChild(wymcontainers_list);

				for (var i = 0; i < containers.length; ++i) {
					var item = containers[i];
					if (typeof(item.tag) === "undefined") {
						continue;
					}
					wymcontainers_list.appendChild(createToolElement(item, " "));
				}

				var wym_top_toolbar = document.createElement("div");
				wym_top_toolbar.className = "wym_top_toolbar";
				wymtools.appendChild(wym_top_toolbar);
				var wymtools_list = document.createElement("ul");
				wymtools_list.className = "wym_toolbar_group first last btn-group";
				wym_top_toolbar.appendChild(wymtools_list);

				for (var i = 0; i < tools.length; ++i) {
					var tool = tools[i];
					if (typeof(tool.tag) === "undefined") {
						continue;
					}
					wymtools_list.appendChild(createToolElement(tool, " btn"));
				}
			}
		}
		xmlhttp.send(null);
	};

	this.unload = function() {
		if (wymbox != undefined) {
			element.parentNode.removeChild(wymbox);
		}
	};
};


var raw_plugin = function()
{
	this.load = function() {};
	this.unload = function() {};
};


var createEditorSwitch = function(element, settings) {
	var currentPlugin = undefined;

	var editors = [
		{
			'id': '',
			'name': 'Žiaden vizuálny editor',
			'plugin': shakal_plugin
		},
		{
			'id': 'wymeditor',
			'name': 'WYMEditor',
			'plugin': wymeditor_plugin
		},
		{
			'id': 'raw',
			'name': 'RAW',
			'plugin': raw_plugin
		}
	];
	var functions = {};

	var div = document.createElement('div');
	div.className = "btn settings";

	var span = document.createElement('span');
	span.innerHTML = '<a href="#" class="settings">Nastavenia</a>';

	var list = document.createElement('ul');
	list.className = 'dropdown menu';

	for (var i = 0; i < editors.length; ++i) {
		var id = editors[i]['id'];
		var editor = editors[i]['name'];
		var plugin = editors[i]['plugin'];
		var li = document.createElement('li');
		var link = document.createElement('a');
		var text = document.createTextNode(editor);
		link.href = '#';
		var change_fn = function(id, editor, plugin) {
			return function() {
				if (currentPlugin != undefined && currentPlugin.id == id) {
					return;
				}
				if (id != "raw") {
					cookiemanager.deleteCookie('last_editor');
					cookiemanager.setCookie('last_editor', id, 365 * 5);
				}
				if (currentPlugin != undefined) {
					currentPlugin.unload();
					currentPlugin = undefined;
				}
				if (plugin != undefined) {
					currentPlugin = new plugin(element, settings);
					currentPlugin.id = id;
					currentPlugin.load();
				}
			}
		} (id, editor, plugin);
		functions[id] = change_fn;
		link.onclick = change_fn;
		link.appendChild(text);
		li.appendChild(link);
		if (id != "raw") {
			list.appendChild(li);
		}
	}

	div.appendChild(span);
	div.appendChild(list);

	element.parentNode.insertBefore(div, element);
	return functions;
}

function initialize_rich_editor(name, settings) {
	"use strict";

	var default_editor = 'wymeditor';
	var editor = cookiemanager.getCookie('last_editor');
	if (settings.force_editor != undefined) {
		editor = settings.force_editor;
	}
	var element = document.getElementById('id_' + name);

	var loadFunctions = createEditorSwitch(element, settings);
	if (loadFunctions[editor] != undefined) {
		loadFunctions[editor]();
	}
	else {
		loadFunctions[default_editor]();
	}

	if (window.rich_editors == undefined) {
		window.rich_editors = {};
	}
	window.rich_editors[name] = {loadFunctions: loadFunctions};
}
*/

(function (_) {

var SimpleEditorHtml = function(element, options) {
	var chrome = _.createDiv('richedit_chrome');
	var inner = _.createDiv('richedit_inner');
	var top = _.createDiv('richedit_top');
	var contents = _.createDiv('richedit_contents');
	var bottom = _.createDiv('richedit_bottom');
	var toolbox = _.createDiv('richedit_toolbox');

	chrome.appendChild(inner);
	inner.appendChild(top);
	inner.appendChild(contents);
	inner.appendChild(bottom);
	top.appendChild(toolbox);

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
		if (btn.options.tag_pre) {
			insert(btn.options.tag_pre, btn.options.tag_post);
		}
		else {
			insert('<' + btn.options.tag + '>', '</' + btn.options.tag + '>');
		}
	};

	var addText = function(btn) {
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

	var insert = function(pre, post) {
		element.focus();
		if (document.selection) {
			var sel = document.selection.createRange();
			sel.text = pre + sel.text + post;
			sel.moveEnd('character', -pre.length);
			sel.select();
		}
		else {
			if (element.selectionStart != undefined) {
				var start = element.selectionStart;
				var end = element.selectionEnd;
				var selection = element.value.substring(start,end);
				element.value = element.value.substring(0, start) + pre + selection + post + element.value.substring(end, element.value.length);
				element.setSelectionRange(start + pre.length, start + pre.length);
			}
			else {
				element.focus();
				element.value = element.value + pre + post;
			}
		}
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
	addButton(tb, {cls: 'icon-templates', onclick: addText}); // pre
	addButton(tb, {cls: 'icon-pastetext', onclick: addText});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-bulletedlist', tag_pre: '<ul>\n<li>', tag_post: '</li>\n</ul>', onclick: triggerFunction});
	addButton(tb, {cls: 'icon-numberedlist', tag_pre: '<ol>\n<li>', tag_post: '</li>\n</ol>', onclick: triggerFunction});

	var tb = addToolbar();
	addButton(tb, {cls: 'icon-link', onclick: addLink});
	addButton(tb, {cls: 'icon-table', tag_pre: '<table>\n<tr><th>', tag_post: '</th><th></th></tr>\n<tr><td></td><td></td></tr>\n</table>', onclick: triggerFunction});
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

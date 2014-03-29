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

	this.load = function()
	{
		loader([settings.static_base + 'js/jquery-1.8.3.min.js'], function() {
			loader([settings['script_wymeditor']], function() {
				jQuery(element).wymeditor({
					skin: 'shakal',
					lang: settings['lang'],
					statusHtml: '',
					updateSelector: jQuery(element).parents('form:first'),
					updateEvent: 'submit',
					postInit: function(wym) {
						editor = wym;
						//wym.table();
					},
					toolsItems: filterTools(all_tools, settings.tags.known),
					containersItems: filterTools(all_containers, settings.tags.known),
					toolsItemHtml: String() +
						'<li class="' + WYMeditor.TOOL_CLASS + ' btn" onclick="this.childNodes[0].childNodes[0].click()">' +
							'<span>' +
								'<a href="#" name="' + WYMeditor.TOOL_NAME + '" ' +
									'title="' + WYMeditor.TOOL_TITLE + '">' +
									WYMeditor.TOOL_TITLE +
								'</a>' +
							'</span>' +
						'</li>'
				});
				var iframe = element.parentNode.getElementsByTagName('iframe')[0];
				var old_onload = iframe.onload;
				iframe.onload = function(event) {
					this.onload = old_onload;
					this.onload(event);
					generate_unsupported_tags(iframe, settings.tags.unsupported);
				};
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

		var tools = filterTools(all_tools, settings.tags.known);
		var containers = filterTools(all_containers, settings.tags.known);
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
							window.event.cancelBubble = true;
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
				cookiemanager.setCookie('last_editor', id, 365 * 5);
				if (currentPlugin != undefined) {
					currentPlugin.unload();
					currentPlugin = undefined;
				}
				if (plugin != undefined) {
					currentPlugin = new plugin(element, settings);
					currentPlugin.load();
				}
			}
		} (id, editor, plugin);
		functions[id] = change_fn;
		link.onclick = change_fn;
		link.appendChild(text);
		li.appendChild(link);
		list.appendChild(li);
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
	var element = document.getElementById('id_' + name);

	var loadFunctions = createEditorSwitch(element, settings);
	if (loadFunctions[editor] != undefined) {
		loadFunctions[editor]();
	}
	else {
		loadFunctions[default_editor]();
	}
}

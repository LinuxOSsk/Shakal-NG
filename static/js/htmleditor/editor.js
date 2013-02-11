function setCookie(name, value, expiredays) {
	var expires = new Date();
	expires.setDate(expires.getDate() + expiredays);
	document.cookie = name + '=' + escape(value) + '; expires=' + expires.toUTCString();
}

function getCookie(requested_name, default_value) {
	var cookies = document.cookie.split(";");
	for (var i = 0; i < cookies.length; ++i) {
		var name = cookies[i].substr(0, cookies[i].indexOf('='));
		var value = cookies[i].substr(cookies[i].indexOf('=') + 1);
		name = name.replace(/^\s+|\s+$/g,"");
		if (name == requested_name) {
			return unescape(value);
		}
	}
	return default_value;
}

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
	var startEditor = function()
	{
		all_tools = [
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
			{name:"CreateLink",title:"Link",css:"wym_tools_link",tag:"a"},
			{name:"Unlink",title:"Unlink",css:"wym_tools_unlink",tag:"a"},
			{name:"InsertImage",title:"Image",css:"wym_tools_image",tag:"img"},
			//{name:"InsertTable",title:"Table",css:"wym_tools_table",tag:"table"},
			{name:"Paste",title:"Paste_From_Word",css:"wym_tools_paste"},
			{name:"ToggleHtml",title:"HTML",css:"wym_tools_html"},
			{name:"Preview",title:"Preview",css:"wym_tools_preview"}
		];
		all_containers = [
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
		}
	}

	var loadEditor = function ()
	{
		var link = document.getElementsByTagName('link')[0];
		if (typeof WYMeditor !== 'undefined') {
			startEditor();
		}
		else {
			script = document.createElement('script');
			script.setAttribute('src', settings['script_wymeditor']);
			script.type = 'text/javascript';
			script.async = true;
			script.onload = function () {
				startEditor();
			};
			link.parentNode.appendChild(script);
		}
	}

	this.load = function()
	{
		(function() {
			if (typeof jQuery !== 'undefined') {
				loadEditor();
			}
			else {
				var link = document.getElementsByTagName('link')[0];
				var script = document.createElement('script');
				script.src = 'http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.js';
				script.type = 'text/javascript';
				script.async = true;
				script.onload = loadEditor;
				link.parentNode.appendChild(script);
			}
		})();
	}

	this.unload = function()
	{
		if (editor != undefined) {
			editor.update();
		}
		element.style.display = 'block';
		var editor_div = element.parentNode.getElementsByTagName('div')[1];
		editor_div.parentNode.removeChild(editor_div);
	}
};

var createEditorSwitch = function(element, settings) {
	var currentPlugin = undefined;

	var editors = [
		{
			'id': 'wymeditor',
			'name': 'WYMEditor',
			'plugin': wymeditor_plugin
		},
		{
			'id': '',
			'name': 'Žiaden vizuálny editor',
			'plugin': undefined
		}
	];
	var functions = {};

	var div = document.createElement('div');
	div.className = "btn settings";
	var span = document.createElement('span');
	span.innerHTML = '<a href="#" class="settings">Nastavenia</a>';
	div.appendChild(span);
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
				setCookie('last_editor', id, 365);
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
	div.appendChild(list);
	element.parentNode.insertBefore(div, element);
	return functions;
}

function initialize_html_editor(name, settings) {
	var default_editor = 'wymeditor';
	var element = document.getElementById('id_' + name);
	var loadFunctions = createEditorSwitch(element, settings);
	var editor = getCookie('last_editor');
	if (loadFunctions[editor] != undefined) {

		loadFunctions[editor]();
	}
	else {
		loadFunctions[default_editor]();
	}
}

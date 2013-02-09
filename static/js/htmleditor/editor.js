var generate_unsupported_tags = function(frame, unsupported_tags) {
	console.log(frame);
	var doc = frame.contentDocument;
	console.log(doc);
	var styleEl = doc.createElement('style');
	styleEl.type = 'text/css';
	var style = doc.createTextNode(unsupported_tags.join(', ') + '{ background-color: #ff9999 !important; border: 1px solid red !important; font-size: 12px !important; font-weight: normal; }');
	styleEl.appendChild(style);
	var link = doc.getElementsByTagName('link')[0];
	link.parentNode.appendChild(styleEl);
};

var wymeditor_plugin = function(element, settings) {
	var startEditor = function()
	{
		jQuery(element).wymeditor({
			skin: 'shakal',
			lang: settings['lang'],
			statusHtml: '',
			updateSelector: jQuery('#id_{{ name }}').parents('form:first'),
			updateEvent: 'submit',
			postInit: function(wym) {
				//wym.table();
			},
			toolsItems: [
				{name:"Undo",title:"Undo",css:"wym_tools_undo"},
				{name:"Redo",title:"Redo",css:"wym_tools_redo"},
				{name:"Bold",title:"Strong",css:"wym_tools_strong"},
				{name:"Italic",title:"Emphasis",css:"wym_tools_emphasis"},
				//{name:"Superscript",title:"Superscript",css:"wym_tools_superscript"},
				//{name:"Subscript",title:"Subscript",css:"wym_tools_subscript"},
				{name:"InsertOrderedList",title:"Ordered_List",css:"wym_tools_ordered_list"},
				{name:"InsertUnorderedList",title:"Unordered_List",css:"wym_tools_unordered_list"},
				{name:"Indent",title:"Indent",css:"wym_tools_indent"},
				{name:"Outdent",title:"Outdent",css:"wym_tools_outdent"},
				{name:"CreateLink",title:"Link",css:"wym_tools_link"},
				{name:"Unlink",title:"Unlink",css:"wym_tools_unlink"},
				{name:"InsertImage",title:"Image",css:"wym_tools_image"},
				//{name:"InsertTable",title:"Table",css:"wym_tools_table"},
				//{name:"Paste",title:"Paste_From_Word",css:"wym_tools_paste"},
				{name:"ToggleHtml",title:"HTML",css:"wym_tools_html"},
				{name:"Preview",title:"Preview",css:"wym_tools_preview"}
			]
		});
		var iframe = element.parentNode.getElementsByTagName('iframe')[0];
		var old_onload = iframe.onload;
		iframe.onload = function(event) {
			this.onload = old_onload;
			this.onload(event);
			generate_unsupported_tags(iframe, settings.unsupported_tags);
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
		element.style.display = 'block';
		var editor_div = element.parentNode.getElementsByTagName('div')[0];
		editor_div.parentNode.removeChild(editor_div);
	}
};

function initialize_html_editor(name, settings) {
	var element = document.getElementById('id_' + name);
	var plugin = new wymeditor_plugin(element, settings);
	plugin.load();
}

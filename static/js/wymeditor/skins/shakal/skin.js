WYMeditor.SKINS['shakal'] = {

	init: function(wym) {
		jQuery(wym._box).find(wym._options.classesSelector)
			.addClass("wym_panel");

		jQuery(wym._box).find(wym._options.toolsSelector)
			.addClass("wym_buttons");

		jQuery(wym._box).find(wym._options.containersSelector)
			.addClass("wym_panel");

		//jQuery(wym._box).find(".wym_tools_emphasis").wrapAll("<div class=\"wym_toolbar_group\"></div>");
		jQuery(wym._box).find("ul").wrap("<div class=\"wym_top_toolbar\"></div>");
		jQuery(wym._box).find(".wym_area_top li").unwrap();
		jQuery(wym._box).find(".wym_tools_undo, .wym_tools_redo").wrapAll("<ul class=\"wym_toolbar_group first btn-group\"></ul>");
		jQuery(wym._box).find(".wym_tools_emphasis, .wym_tools_strong, .wym_tools_superscript, .wym_tools_subscript").wrapAll("<ul class=\"wym_toolbar_group btn-group\"></ul>");
		jQuery(wym._box).find(".wym_tools_ordered_list, .wym_tools_unordered_list, .wym_tools_indent, .wym_tools_outdent").wrapAll("<ul class=\"wym_toolbar_group btn-group\"></ul>");
		//jQuery(wym._box).find(".wym_tools_link, .wym_tools_unlink").wrapAll("<ul class=\"wym_toolbar_group\"></ul>");
		jQuery(wym._box).find(".wym_tools_link, .wym_tools_unlink").wrapAll("<ul class=\"wym_toolbar_group btn-group\"></ul>");
		jQuery(wym._box).find(".wym_tools_image").wrapAll("<ul class=\"wym_toolbar_group btn-group\"></ul>");
		jQuery(wym._box).find(".wym_tools_html, .wym_tools_preview, .wym_tools_paste").wrapAll("<ul class=\"wym_toolbar_group last btn-group\"></ul>");

		jQuery(wym._box).find("div.wym_area_right h2").wrap("<div class=\"btn\" />");
		jQuery(wym._box).find("div.wym_area_right h2").each(function() {
			jQuery("<span><span class=\"dropdown\">" + jQuery(this).html() + "<span class=\"icon\"></span></span></span>").replaceAll(this);
		});
		jQuery(wym._box).find("div.wym_area_right > *")
			.remove()
			.prependTo(jQuery(wym._box).find("div.wym_area_top"));

		// auto add some margin to the main area sides if left area
		// or right area are not empty (if they contain sections)
		jQuery(wym._box).find("div.wym_area_right ul")
			.parents("div.wym_area_right").show()
			.parents(wym._options.boxSelector)
			.find("div.wym_area_main")
			.css({"margin-right": "205px"});

		jQuery(wym._box).find("div.wym_area_left ul")
			.parents("div.wym_area_left").show()
			.parents(wym._options.boxSelector)
			.find("div.wym_area_main")
			.css({"margin-left": "205px"});

		//make hover work under IE < 7
		jQuery(wym._box).find(".wym_section").hover(function(){
			jQuery(this).addClass("hover");
		},function(){
			jQuery(this).removeClass("hover");
		});
	}
};

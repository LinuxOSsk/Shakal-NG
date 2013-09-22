jQuery(function($) {
	var statsContainer = $('.stats');
	var statsLink = $('a', statsContainer).last();
	var statsContent = $('.dashboard-module-content', statsContainer);

	var loadTabContent = function(tab) {
		var container = tab.parentNode;
		var module_id = tab.id.replace(/_stats_chart$/, "");
		var selectVal = $('select', container.parentNode).val();
		if (!selectVal) {
			return;
		}

		var loadGraphFunction = function(tabNode, url) {
			return function() {
				return new Dygraph(tabNode, url + "&format=csv");
			}
		}(tab, selectVal);
		setTimeout(loadGraphFunction, 100);
	}

	var processStats = function(data) {
		var groupTabs = $('<div class="group group-tabs"></div>');
		statsContent.append(groupTabs);
		//var tabs = $('<ul></ul>');
		var tabs = $('<ul id="suit_form_tabs" class="nav nav-tabs nav-tabs-suit" data-tab-prefix="suit-tab"></ul>');
		groupTabs.append(tabs);

		for (var j = 0; j < data.length; ++j) {
			var id = data[j][0];
			var info = data[j][1];
			var choices = info.choices;
			var tab = $('<li class="group-tabs-link"></li>');
			var tabLink = $('<a href="#module_' + id + '"></a>');
			tabLink.text(info.name);
			tab.append(tabLink);
			tabs.append(tab);

			//var submodule = $('<div id="module_' + id + '" class="dashboard-module"></div>');
			var submodule = $('<div id="module_' + id + '" class="dashboard-module suit-tab suit-tab-module_' + id + ' well" style="margin-top: -15px;"></div>');
			groupTabs.append(submodule);

			var sel = $('<select></select>');
			for (var i = 0; i < choices.length; ++i) {
				var choice = choices[i];
				var opt = $('<option></option>');
				opt.attr('value', choice.url);
				opt.text(choice.label);
				sel.append(opt);
			}
			submodule.append(sel);

			var submoduleContent = $('<div class="dashboard-module-content"></div>');
			submodule.append(submoduleContent);
			var chart = $('<div id="' + id + '" class="stats_chart" style="height: 200px;"></div>');
			submoduleContent.append(chart);

			sel.bind('change', (function(chart) { return function() { loadTabContent(chart); };} )(chart[0]));
		}

		//$('.stats .group-tabs').tabs();
		$('#suit_form_tabs').find("a").click(function() {
			loadTabContent($('.suit-tab' + $(this).attr('href').replace("#", "-") + ' .stats_chart')[0]);
		});
		$('#suit_form_tabs').suit_form_tabs();
		//$('.stats .group-tabs').bind('tabsactivate', function(event, ui) { loadTabContent($('.stats_chart', ui.newPanel)[0]); });
		//loadTabContent($('.stats_chart')[0]);
	};

	var loadStats = function() {
		var statsHref = statsLink.attr('href');
		statsLink.remove();
		$.getJSON(statsHref, processStats);
	};

	loadStats();
});

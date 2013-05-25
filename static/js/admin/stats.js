jQuery(window).load(function() {
	var $ = jQuery;

	var loadTabContent = function(tab) {
		var container = tab.parentNode;
		var module_id = tab.id.replace(/_stats_chart$/, "");
		var selectVal = $('select', container.parentNode).val();
		if (!selectVal) {
			return;
		}
		var chart = new google.visualization.LineChart(tab);
		jQuery.getJSON(selectVal, function(data) {
			chart.draw(google.visualization.arrayToDataTable(data), {legend: {position: 'none'}, chartArea: {width: '85%', height: '65%'}});
		});
	};

	var loadStats = function() {
		var statsContainer = $('.stats');
		var statsLink = $('a', statsContainer).last();
		var statsContent = $('.dashboard-module-content', statsContainer);
		var statsHref = statsLink.attr('href');
		statsLink.remove();
		var data;
		$.ajax({
			type: 'GET',
			url: statsHref,
			dataType: 'json',
			success: function(d) { data = d; },
			data: {},
			async: false
		});


		var groupTabs = $('<div class="group group-tabs"></div>');
		statsContent.append(groupTabs);
		var tabs = $('<ul></ul>');
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

			var submodule = $('<div id="module_' + id + '" class="dashboard-module"></div>');
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
			var chart = $('<div id="' + id + '" class="stats_chart" style="height: 300px;"></div>');
			submoduleContent.append(chart);

			sel.bind('change', (function(chart) { return function() { loadTabContent(chart); };} )(chart[0]))
		}

		$('.stats .group-tabs').tabs();
		$('.stats .group-tabs').bind('tabsactivate', function(event, ui) { loadTabContent($('.stats_chart', ui.newPanel)[0]); });
		loadTabContent($('.stats_chart')[0]);
	}

	var s = document.createElement('script');
	s.type = 'text/javascript';
	s.async = true;
	s.src = 'https://www.google.com/jsapi';
	s.onload = s.onreadystatechange = function() {
		var loadCallback = function() {
			loadStats();
		};
		var options = {packages: ['corechart'], callback : loadCallback};
		google.load('visualization', '1', options);
	};
	var x = document.getElementsByTagName('script')[0];
	x.parentNode.insertBefore(s, x);
});

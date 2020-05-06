(function() {
document.addEventListener("DOMContentLoaded", function() {

var statsContainer = document.querySelector('.stats');
if (statsContainer === null) {
	return;
}
var statsLink = statsContainer.getElementsByTagName('a')[0];
if (statsLink === undefined) {
	return;
}
var statsContent = statsContainer.querySelector('.dashboard-module-content');
if (statsContent === null) {
	return;
}


function loadTabContent(tab) {
	var container = tab.parentNode.parentNode;
	var module_id = tab.id.replace(/_stats_chart$/, "");
	var select = container.getElementsByTagName('select')[0];
	var selectVal = select.value;
	if (!selectVal) {
		return;
	}

	var loadGraphFunction = function(tabNode, url) {
		return function() {
			return new Dygraph(tabNode, url + "&format=csv");
		};
	}(tab, selectVal);
	setTimeout(loadGraphFunction, 100);
}


function processStats(data) {
	var groupTabs = document.createElement('div');
	groupTabs.className = 'group group-tabs stats';
	statsContent.appendChild(groupTabs);
	var tabs = document.createElement('ul');
	tabs.setAttribute('id', 'suit_form_tabs');
	tabs.className = 'nav nav-tabs nav-tabs-suit';
	tabs.setAttribute('data-tab-prefix', 'suit-tab');
	groupTabs.appendChild(tabs);

	data.forEach(function(group) {
		var id = group[0];
		var info = group[1];
		var choices = info.choices;
		var tab = document.createElement('li');
		tab.className = 'group-tabs-link';
		var tabLink = document.createElement('a');
		tabLink.setAttribute('href', '#module_' + id);
		tabLink.appendChild(document.createTextNode(info.name));
		tab.appendChild(tabLink);
		tabs.appendChild(tab);

		var submodule = document.createElement('div');
		submodule.setAttribute('id', 'module_' + id);
		submodule.className = 'dashboard-module suit-tab suit-tab-module_' + id + ' well';
		groupTabs.appendChild(submodule);

		var sel = document.createElement('select');
		for (var i = 0; i < choices.length; ++i) {
			var choice = choices[i];
			var opt = document.createElement('option');
			opt.setAttribute('value', choice.url);
			opt.appendChild(document.createTextNode(choice.label));
			sel.append(opt);
		}
		submodule.appendChild(sel);

		var submoduleContent = document.createElement('div');
		submoduleContent.className = 'dashboard-module-content';
		submodule.appendChild(submoduleContent);
		var chart = document.createElement('div');
		chart.setAttribute('id', id + '_stats_chart');
		chart.className = 'stats-chart';
		submoduleContent.appendChild(chart);

		sel.onchange = (function(chart) { return function() { loadTabContent(chart); };} )(chart);
	});

	tabs.onclick = function(e) {
		var target = e.target;
		if (target.tagName.toLowerCase() === 'a') {
			var id = target.getAttribute('href').slice(8);
			var tab = document.getElementById(id + '_stats_chart');
			loadTabContent(tab);
			e.preventDefault();
		}
	};

	loadTabContent(groupTabs.querySelector('.stats-chart'));
}


function loadStats() {
	var statsHref = statsLink.getAttribute('href');
	statsLink.remove();
	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4 && xhr.status == 200) {
			var json = JSON.parse(xhr.responseText);
			processStats(json);
		}
	};
	xhr.open("GET", statsHref, true);
	xhr.send(null);
}


loadStats();
});
}());

(function (_) {

var HSVtoRGB = function(h, s, v) {
	var r, g, b, i, f, p, q, t;
	if (arguments.length === 1) {
		s = h.s;
		v = h.v;
		h = h.h;
	}
	i = Math.floor(h * 6);
	f = h * 6 - i;
	p = v * (1 - s);
	q = v * (1 - f * s);
	t = v * (1 - (1 - f) * s);
	switch (i % 6) {
		case 0: r = v; g = t; b = p; break;
		case 1: r = q; g = v; b = p; break;
		case 2: r = p; g = v; b = t; break;
		case 3: r = p; g = q; b = v; break;
		case 4: r = t; g = p; b = v; break;
		case 5: r = v; g = p; b = q; break;
	}
	return {
		r: Math.round(r * 255),
		g: Math.round(g * 255),
		b: Math.round(b * 255)
	};
};

var RGBtoHSV = function(r, g, b) {
	if (arguments.length === 1) {
		g = r.g;
		b = r.b;
		r = r.r;
	}
	var max = Math.max(r, g, b), min = Math.min(r, g, b),
		d = max - min,
		h,
		s = (max === 0 ? 0 : d / max),
		v = max / 255;

	switch (max) {
		case min: h = 0; break;
		case r: h = (g - b) + d * (g < b ? 6: 0); h /= 6 * d; break;
		case g: h = (b - r) + d * 2; h /= 6 * d; break;
		case b: h = (r - g) + d * 4; h /= 6 * d; break;
	}

	return {
		h: h,
		s: s,
		v: v
	};
};

var BarChartPlotter = function(e) {
	var ctx = e.drawingContext;
	var points = e.points;
	var y_bottom = e.dygraph.toDomYCoord(0);

	var i;
	var bar_width = 1;
	var xmin = points[0].xval;
	var xmax = points[points.length - 1].xval;
	var xdiff = xmax - xmin;
	for (i = 0; i < points.length - 1; i++) {
		xdiff = Math.min(points[i+1].xval - points[i].xval, xdiff);
	}
	bar_width = 2/3 * (points[1].canvasx - points[0].canvasx) * (xdiff / (points[1].xval - points[0].xval));

	var color = new RGBColorParser(e.color);
	color.r = Math.floor((255 + color.r) / 2);
	color.g = Math.floor((255 + color.g) / 2);
	color.b = Math.floor((255 + color.b) / 2);
	ctx.fillStyle = color.toRGB();

	for (i = 0; i < points.length; i++) {
		var p = points[i];
		var center_x = p.canvasx;

		ctx.fillRect(center_x - bar_width / 2, p.canvasy, bar_width, y_bottom - p.canvasy);
		ctx.strokeRect(center_x - bar_width / 2, p.canvasy, bar_width, y_bottom - p.canvasy);
	}
};

var calcColor = function(val) {
	var left = [0.1, 0.1, 0.98];
	var mid = [0.2975, 1.00, 0.965];
	var right = [0.2975, 1.0, 0.2];
	var pos, rpos, rgb;

	if (val < 0.5) {
		pos = val * 2;
		rpos = 1.0 - pos;
		rgb = HSVtoRGB(mid[0] * pos + left[0] * rpos, mid[1] * pos + left[1] * rpos, mid[2] * pos + left[2] * rpos);
	}
	else {
		pos = (val - 0.5) * 2;
		rpos = 1.0 - pos;
		rgb = HSVtoRGB(right[0] * pos + mid[0] * rpos, right[1] * pos + mid[1] * rpos, right[2] * pos + mid[2] * rpos);
	}

	return 'rgb(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ')';
};

var countWeeks = 0;
var maxDayValue = 0;

daily_stats.forEach(function(day, i) {
	if (day[0][3] === 0 || i === 0) {
		countWeeks++;
	}
	maxDayValue = Math.max(maxDayValue, day[1]);
});

var weekPercentWidth = 100 / (countWeeks + 1);
var dailyStatsContainer = _.id('daily_stats');
var currentColumn;
var transparentImg = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';

var columnOuter = document.createElement('DIV');
columnOuter.style.float = 'left';
columnOuter.style.width = (weekPercentWidth * 1) + '%';
columnOuter.style.minHeight = '1px';
dailyStatsContainer.appendChild(columnOuter);

var days = ['', 'PO', 'UT', 'ST', 'ŠT', 'PI', 'SO', 'NE'];
var months = ['JAN', 'FEB', 'MAR', 'APR', 'MÁJ', 'JÚN', 'JÚL', 'AUG', 'SEP', 'OKT', 'NOV', 'DEC'];

var createTextBlock = function(text) {
	var block = document.createElement('DIV');
	block.style.position = 'relative';

	var span = document.createElement('SPAN');
	span.style.position = 'absolute';
	span.style.color = '#888888';
	span.style.top = '50%';
	span.style.marginTop = '-4px';
	span.style.fontSize = '8px';
	span.innerHTML = text;
	block.appendChild(span);

	var img = document.createElement('IMG');
	img.style.width = '100%';
	img.style.display = 'block';
	img.src = transparentImg;

	block.appendChild(img);
	return block;
};

for (var i = 0; i < 8; ++i) {
	columnOuter.appendChild(createTextBlock(days[i]));
}

var currentMonth;
var currentDay = current_day;
if (currentDay !== undefined) {
	currentDay = current_day.split('-');
	currentDay[0] = parseInt(currentDay[0], 10);
	currentDay[1] = parseInt(currentDay[1], 10);
	currentDay[2] = parseInt(currentDay[2], 10);
}

daily_stats.forEach(function(day, i) {
	if (currentColumn === undefined || day[0][3] === 0) {
		var isFirst = currentColumn === undefined;
		var columnOuter = document.createElement('DIV');
		columnOuter.style.float = 'left';
		columnOuter.style.width = weekPercentWidth + '%';
		columnOuter.style.minHeight = '1px';
		dailyStatsContainer.appendChild(columnOuter);

		currentColumn = document.createElement('DIV');
		if (isFirst) {
			currentColumn.style.position = 'absolute';
			currentColumn.style.bottom = '0px';
			currentColumn.style.width = weekPercentWidth + '%';
		}
		else {
			if (currentMonth !== day[0][1]) {
				if (i > 14) {
					currentMonth = day[0][1];
					var span = document.createElement('SPAN');
					span.style.position = 'absolute';
					span.style.color = '#888888';
					span.style.top = '0';
					span.style.fontSize = '8px';
					span.innerHTML = months[currentMonth - 1];
					currentColumn.appendChild(span);
				}
			}
		}
		columnOuter.appendChild(currentColumn);
		currentColumn.appendChild(createTextBlock(''));
	}

	var block = document.createElement('DIV');
	/*
	block.style.background = '#eeeeee';
	if (day[1]) {
		block.style.background = calcColor(day[1] / maxDayValue);
	}
	*/
	if (day[1]) {
		block.className = 'block a-' + Math.round(day[1] / maxDayValue * 20);
	}
	else {
		block.className = 'block';
	}

	var time = day[0];
	var title = '';
	switch (time[3]) {
		case 0: title = 'Pondelok'; break;
		case 1: title = 'Utorok'; break;
		case 2: title = 'Streda'; break;
		case 3: title = 'Štvrtok'; break;
		case 4: title = 'Piatok'; break;
		case 5: title = 'Sobota'; break;
		case 6: title = 'Nedeľa'; break;
	}
	title += ' ' + time[2] + '. ' + time[1] + '. ' + time[0];
	var img = document.createElement('IMG');
	img.style.width = '100%';
	img.style.display = 'block';
	img.src = transparentImg;
	img.setAttribute('title', title + ' - ' + day[1]);

	if (day[1]) {
		var link = document.createElement('a');
		link.setAttribute('href', current_path + '?day=' + time[0] + '-' + time[1] + '-' + time[2]);
		if (currentDay !== undefined) {
			if (currentDay[0] != time[0] || currentDay[1] != time[1] || currentDay[2] != time[2]) {
				block.style.opacity = 0.5;
			}
			else {
				block.style.borderColor = '#888';
				link.setAttribute('href', current_path);
			}
		}
		link.appendChild(img);
		block.appendChild(link);
	}
	else {
		block.appendChild(img);
	}
	currentColumn.appendChild(block);
});

var monthlyStatsContainer = _.id('monthly_stats');
if (monthly_stats.length < 2) {
	monthlyStatsContainer.parentNode.parentNode.style.display = "none";
	return;
}

var skip = true;
var data = [];
monthly_stats.forEach(function(day, i) {
	if (day[1] == 0 && skip) {
		return;
	}
	var date = new Date(day[0][0], day[0][1] - 1, day[0][2]);
	data.push([date, day[1]]);
	skip = false;
});

var opts = {
	plotter: BarChartPlotter,
	axes: {
		x: {
			valueFormatter: Dygraph.dateString_,
			ticker: Dygraph.dateTicker
		}
	},
	labels: ['Dátum', 'Počet']
};
var graph = new Dygraph(monthlyStatsContainer, data, opts);

}(_utils2));

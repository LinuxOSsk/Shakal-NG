(function(_) {


var toggle = function(options) {
	var self = {};
	self.options = _.lightCopy(options || {});
	self.options.containerClass = self.options.containerClass === undefined ? 'toggle' : self.options.containerClass;
	self.options.togglerClass = self.options.togglerClass === undefined ? 'toggle' : self.options.togglerClass;
	self.options.classes = self.options.classes === undefined ? ['toggled', ''] : self.options.classes;
	self.options.onBeforeToggle = self.options.onBeforeToggle === undefined ? function(element, cls) {} : self.options.onBeforeToggle;
	self.options.onAfterToggle = self.options.onAfterToggle === undefined ? function(element, cls) {} : self.options.onAfterToggle;

	var onBodyClicked = function(e) {
		if (e.which !== 1) {
			return;
		}

		if (self.options.classes.length < 2) {
			return;
		}

		var element = e.target;
		if (!_.hasClass(element, self.options.togglerClass)) {
			element = _.findParentByCls(element, self.options.togglerClass);
			if (element === null) {
				return;
			}
		}

		var container = element;
		if (!_.hasClass(container, self.options.containerClass)) {
			container = _.findParentByCls(container, self.options.containerClass);
			if (container === null) {
				return;
			}
		}

		e.preventDefault();
		onToggleClicked(container);
	};

	var onToggleClicked = function(element) {
		var currentCls = -1;
		var emptyCls = -1;
		_.forEach(self.options.classes, function(cls, idx) {
			if (cls === '') {
				emptyCls = idx;
			}
			else {
				if (_.hasClass(element, cls)) {
					currentCls = idx;
				}
			}
		});
		if (currentCls === -1) {
			if (emptyCls === -1) {
				currentCls = self.options.classes.length - 1;
			}
			else {
				currentCls = emptyCls;
			}
		}
		var nextCls = (currentCls + 1) % self.options.classes.length;
		self.options.onBeforeToggle(element, self.options.classes[nextCls]);
		var className = self.options.classes[currentCls];
		if (className !== '') {
			_.removeClass(element, className);
		}
		className = self.options.classes[nextCls];
		if (className !== '') {
			_.addClass(element, self.options.classes[nextCls]);
		}
		self.options.onAfterToggle(element, self.options.classes[nextCls]);
	};

	_.bindEvent(document.body, 'click', onBodyClicked);
};


_.toggle = toggle;


toggle({
	containerClass: 'foldable-sidebar',
	togglerClass: 'block-title',
	classes: ['open', '']
});


}(_utils));

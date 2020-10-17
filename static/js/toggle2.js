(function(_) {


function onBlockTitleClicked(e, element) {
	if (e.which !== 1) { return; }
	var container = element.closest('.foldable-sidebar');
	if (container !== null) {
		container.classList.toggle('open');
	}
}


_.listen('.block-title', 'click', onBlockTitleClicked);


}(_utils2));

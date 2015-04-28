# -*- coding: utf-8 -*-
from __future__ import unicode_literals

SPRITES = (
	{
		'name': 'main',
		'output': 'desktop/default/images/backgrounds.png',
		'scss_output': 'desktop/default/sprites.scss',
		'extra_sizes': (),
		'width': 800,
		'height': 880,
		'images': (
			{
				'name': 'logo',
				'src': 'desktop/default/images/logo.png',
				'mode': 'no-repeat', 'width': 240, 'height': 80
			},
			{
				'name': 'avatar_placeholder',
				'src': 'desktop/default/images/avatar_placeholder.png',
				'mode': 'no-repeat', 'width': 56, 'height': 56
			},
			{
				'name': 'breadcrumb_bg',
				'src': 'desktop/default/images/breadcrumb_bg.png',
				'mode': 'no-repeat', 'width': 8, 'height': 36
			},
			{
				'name': 'breadcrumb_bg_reverse',
				'src': 'desktop/default/images/breadcrumb_bg_reverse.png',
				'mode': 'no-repeat', 'width': 8, 'height': 36
			},
			{
				'name': 'breadcrumb_home',
				'src': 'desktop/default/images/breadcrumb_home.png',
				'mode': 'no-repeat', 'width': 18, 'height': 18
			},
			{
				'name': 'dropdown_icon_14',
				'src': 'desktop/default/images/dropdown_icon_14.png',
				'mode': 'no-repeat', 'width': 9, 'height': 14
			},
			{
				'name': 'profile_icon_14',
				'src': 'desktop/default/images/profile_icon_14.png',
				'mode': 'no-repeat', 'width': 9, 'height': 14
			},
			{
				'name': 'search_icon',
				'src': 'desktop/default/images/search_icon.png',
				'mode': 'no-repeat', 'width': 32, 'height': 38
			},
			{
				'name': 'rss_icon',
				'src': 'desktop/default/images/rss_icon.png',
				'mode': 'no-repeat', 'width': 32, 'height': 38
			},
			{
				'name': 'trashcan',
				'src': 'desktop/default/images/trashcan.png',
				'mode': 'no-repeat', 'width': 16, 'height': 16
			},
			{
				'name': 'corner_arrow_up',
				'src': 'desktop/default/images/corner_arrow_up.png',
				'mode': 'no-repeat', 'width': 13, 'height': 7
			},
			{
				'name': 'locked_icon',
				'src': 'desktop/default/images/locked.png',
				'mode': 'no-repeat', 'width': 16, 'height': 16
			},
			{
				'name': 'new_icon',
				'src': 'desktop/default/images/new.png',
				'mode': 'no-repeat', 'width': 16, 'height': 16
			},
			{
				'name': 'tick_icon',
				'src': 'desktop/default/images/tick.png',
				'mode': 'no-repeat', 'width': 16, 'height': 16
			},
			{
				'name': 'watch_icon',
				'src': 'desktop/default/images/watch.png',
				'mode': 'no-repeat', 'width': 16, 'height': 16
			},
			{
				'name': 'comment_icon_14',
				'src': 'desktop/default/images/comment_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'watch_icon_14',
				'src': 'desktop/default/images/watch_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'tick_icon_14',
				'src': 'desktop/default/images/tick_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'lock_icon_14',
				'src': 'desktop/default/images/lock_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'up_icon_14',
				'src': 'desktop/default/images/up_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'down_icon_14',
				'src': 'desktop/default/images/down_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'delete_icon_14',
				'src': 'desktop/default/images/delete_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'settings_icon_14',
				'src': 'desktop/default/images/settings_icon_14.png',
				'mode': 'no-repeat', 'width': 16, 'height': 15
			},
			{
				'name': 'header_bg',
				'src': 'desktop/default/images/header_bg.png',
				'mode': 'repeat-x', 'width': 1, 'height': 80
			},
			{
				'name': 'user_rating_0',
				'src': 'desktop/default/images/rating_0.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'user_rating_1',
				'src': 'desktop/default/images/rating_1.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'user_rating_2',
				'src': 'desktop/default/images/rating_2.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'user_rating_3',
				'src': 'desktop/default/images/rating_3.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'user_rating_4',
				'src': 'desktop/default/images/rating_4.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'user_rating_5',
				'src': 'desktop/default/images/rating_5.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'user_rating_admin',
				'src': 'desktop/default/images/rating_admin.png',
				'mode': 'no-repeat', 'width': 20, 'height': 36
			},
			{
				'name': 'btn_std',
				'src': 'desktop/default/images/btn.png',
				'mode': 'no-repeat', 'width': 800, 'height': 38,
			},
			{
				'name': 'btn_std_hover',
				'src': 'desktop/default/images/btn.png',
				'mode': 'no-repeat', 'width': 800, 'height': 38,
			},
			{
				'name': 'btn_act',
				'src': 'desktop/default/images/btn.png',
				'mode': 'no-repeat', 'width': 800, 'height': 38,
			},
			{
				'name': 'btn_act_hover',
				'src': 'desktop/default/images/btn.png',
				'mode': 'no-repeat', 'width': 800, 'height': 38,
			},
			{
				'name': 'btn_content_std',
				'src': 'desktop/default/images/btn_content.png',
				'mode': 'no-repeat', 'width': 800, 'height': 32,
			},
			{
				'name': 'btn_content_std_hover',
				'src': 'desktop/default/images/btn_content.png',
				'mode': 'no-repeat', 'width': 800, 'height': 32,
			},
			{
				'name': 'btn_content_act',
				'src': 'desktop/default/images/btn_content.png',
				'mode': 'no-repeat', 'width': 800, 'height': 32,
			},
			{
				'name': 'btn_content_act_hover',
				'src': 'desktop/default/images/btn_content.png',
				'mode': 'no-repeat', 'width': 800, 'height': 32,
			},
			{
				'name': 'breadcrumb_panel_bg',
				'src': 'desktop/default/images/breadcrumb_panel_bg.png',
				'mode': 'repeat-x', 'width': 1, 'height': 36
			},
			{
				'name': 'breadcrumb_std',
				'src': 'desktop/default/images/breadcrumb.png',
				'mode': 'no-repeat', 'width': 800, 'height': 31,
			},
			{
				'name': 'breadcrumb_act',
				'src': 'desktop/default/images/breadcrumb.png',
				'mode': 'no-repeat', 'width': 800, 'height': 31,
			},
			{
				'name': 'tabs_std',
				'src': 'desktop/default/images/tabs.png',
				'mode': 'no-repeat', 'width': 800, 'height': 33,
			},
			{
				'name': 'tabs_act',
				'src': 'desktop/default/images/tabs.png',
				'mode': 'no-repeat', 'width': 800, 'height': 33,
			},
			{
				'name': 'block_header_bg',
				'src': 'desktop/default/images/block_header_bg.png',
				'mode': 'repeat-x', 'width': 1, 'height': 37
			},
			{
				'name': 'submit_row_bg',
				'src': 'desktop/default/images/submit_row_bg.png',
				'mode': 'repeat-x', 'width': 1, 'height': 41
			},
			{
				'name': 'input_bg',
				'src': 'desktop/default/images/input_bg.png',
				'mode': 'repeat-x', 'width': 1, 'height': 48
			},
			{
				'name': 'progress',
				'src': 'desktop/default/images/progressbar.png',
				'mode': 'repeat-x', 'width': 1, 'height': 14,
			},
			{
				'name': 'progress_bar',
				'src': 'desktop/default/images/progressbar.png',
				'mode': 'repeat-x', 'width': 1, 'height': 14,
			},
		),
	},
)

<?php

require "utils.php";

/**
 * @file
 * Framework for handling filtering of content.
 */

// This is a special format ID which means "use the default format". This value
// can be passed to the filter APIs as a format ID: this is equivalent to not
// passing an explicit format at all.
define('FILTER_FORMAT_DEFAULT', 0);

define('FILTER_HTML_STRIP', 1);
define('FILTER_HTML_ESCAPE', 2);

/**
 * Implementation of hook_help().
 */
function filter_help($section) {
	switch ($section) {
		case 'admin/help#filter':
			$output = '<p>'. t("The filter module allows administrators to configure  text input formats for the site. For example, an administrator may want a filter to strip out malicious HTML from user's comments. Administrators may also want to make URLs linkable even if they are only entered in an unlinked format.") .'</p>';
			$output .= '<p>'. t('Users can choose between the available input formats when creating or editing content. Administrators can configure which input formats are available to which user roles, as well as choose a default input format. Administrators can also create new input formats. Each input format can be configured to use a selection of filters.') .'</p>';
			$output .= '<p>'. t('For more information please read the configuration and customization handbook <a href="@filter">Filter page</a>.', array('@filter' => 'http://drupal.org/handbook/modules/filter/')) .'</p>';
			return $output;

		case 'admin/settings/filters':
			return t('
<p><em>Input formats</em> define a way of processing user-supplied text in Drupal. Every input format has its own settings of which <em>filters</em> to apply. Possible filters include stripping out malicious HTML and making URLs clickable.</p>
<p>Users can choose between the available input formats when submitting content.</p>
<p>Below you can configure which input formats are available to which roles, as well as choose a default input format (used for imported content, for example).</p>
<p>Note that (1) the default format is always available to all roles, and (2) all filter formats can always be used by roles with the "administer filters" permission even if they are not explicitly listed in the Roles column of this table.</p>');

		case 'admin/settings/filters/'. arg(3):
			return t('
<p>Every <em>filter</em> performs one particular change on the user input, for example stripping out malicious HTML or making URLs clickable. Choose which filters you want to apply to text in this input format.</p>
<p>If you notice some filters are causing conflicts in the output, you can <a href="@rearrange">rearrange them</a>.</p>', array('@rearrange' => url('admin/settings/filters/'. arg(3) .'/order')));

		case 'admin/settings/filters/'. arg(3) .'/configure':
			return '<p>'. t('If you cannot find the settings for a certain filter, make sure you have enabled it on the <a href="@url">view tab</a> first.', array('@url' => url('admin/settings/filters/'. arg(3)))) .'</p>';

		case 'admin/settings/filters/'. arg(3) .'/order':
			return t('
<p>Because of the flexible filtering system, you might encounter a situation where one filter prevents another from doing its job. For example: a word in an URL gets converted into a glossary term, before the URL can be converted in a clickable link. When this happens, you will need to rearrange the order in which filters get executed.</p>
<p>Filters are executed from top-to-bottom. You can use the weight column to rearrange them: heavier filters "sink" to the bottom.</p>');
	}
}

/**
 * Implementation of hook_menu().
 */
function filter_menu($may_cache) {
	$items = array();

	if ($may_cache) {
		$items[] = array('path' => 'admin/settings/filters',
			'title' => t('Input formats'),
			'description' => t('Configure how content input by users is filtered, including allowed HTML tags, PHP code tags. Also allows enabling of module-provided filters.'),
			'callback' => 'drupal_get_form',
			'callback arguments' => array('filter_admin_overview'),
			'access' => user_access('administer filters'),
		);
		$items[] = array('path' => 'admin/settings/filters/list',
			'title' => t('List'),
			'callback' => 'filter_admin_overview',
			'type' => MENU_DEFAULT_LOCAL_TASK,
'access' => user_access('administer filters'),
		);
		$items[] = array('path' => 'admin/settings/filters/add',
			'title' => t('Add input format'),
			'callback' => 'drupal_get_form',
			'callback arguments' => array('filter_admin_format_form'),
			'type' => MENU_LOCAL_TASK,
			'weight' => 1,
			'access' => user_access('administer filters'),
		);
		$items[] = array('path' => 'admin/settings/filters/delete',
			'title' => t('Delete input format'),
			'callback' => 'drupal_get_form',
			'callback arguments' => array('filter_admin_delete'),
			'type' => MENU_CALLBACK,
			'access' => user_access('administer filters'),
		);
		$items[] = array('path' => 'filter/tips',
			'title' => t('Compose tips'),
			'callback' => 'filter_tips_long',
			'access' => TRUE,
			'type' => MENU_SUGGESTED_ITEM,
		);
	}
	else {
		if (arg(0) == 'admin' && arg(1) == 'settings' && arg(2) == 'filters' && is_numeric(arg(3))) {
			$formats = filter_formats();

			if (isset($formats[arg(3)])) {
				$items[] = array('path' => 'admin/settings/filters/'. arg(3),
					'title' => t("!format input format", array('!format' => $formats[arg(3)]->name)),
					'callback' => 'drupal_get_form',
					'callback arguments' => array('filter_admin_format_form', $formats[arg(3)]),
					'type' => MENU_CALLBACK,
					'access' => user_access('administer filters'),
				);
				$items[] = array('path' => 'admin/settings/filters/'. arg(3) .'/list',
					'title' => t('View'),
					'callback' => 'drupal_get_form',
					'callback arguments' => array('filter_admin_format_form', $formats[arg(3)]),
					'type' => MENU_DEFAULT_LOCAL_TASK,
					'weight' => 0,
					'access' => user_access('administer filters'),
				);
				$items[] = array('path' => 'admin/settings/filters/'. arg(3) .'/configure',
					'title' => t('Configure'),
					'callback' => 'drupal_get_form',
					'callback arguments' => array('filter_admin_configure'),
					'type' => MENU_LOCAL_TASK,
					'weight' => 1,
					'access' => user_access('administer filters'),
				);
				$items[] = array('path' => 'admin/settings/filters/'. arg(3) .'/order',
					'title' => t('Rearrange'),
					'callback' => 'drupal_get_form',
					'callback arguments' => array('filter_admin_order', 'format' => $formats[arg(3)]),
					'type' => MENU_LOCAL_TASK,
					'weight' => 2,
					'access' => user_access('administer filters'),
				);
			}
		}
	}

	return $items;
}

/**
 * Implementation of hook_perm().
 */
function filter_perm() {
	return array('administer filters');
}

/**
 * Implementation of hook_cron().
 *
 * Expire outdated filter cache entries
 */
function filter_cron() {
	cache_clear_all(NULL, 'cache_filter');
}

/**
 * Implementation of hook_filter_tips().
 */
function filter_filter_tips($delta, $format, $long = FALSE) {
	global $base_url;
	switch ($delta) {
		case 0:
			if (variable_get("filter_html_$format", FILTER_HTML_STRIP) ==  FILTER_HTML_STRIP) {
				if ($allowed_html = variable_get("allowed_html_$format", '<a> <em> <strong> <cite> <code> <ul> <ol> <li> <dl> <dt> <dd>')) {
					switch ($long) {
						case 0:
							return t('Allowed HTML tags: @tags', array('@tags' => $allowed_html));
						case 1:
							$output = '<p>'. t('Allowed HTML tags: @tags', array('@tags' => $allowed_html)) .'</p>';
							if (!variable_get("filter_html_help_$format", 1)) {
								return $output;
							}

							$output .= t('
<p>This site allows HTML content. While learning all of HTML may feel intimidating, learning how to use a very small number of the most basic HTML "tags" is very easy. This table provides examples for each tag that is enabled on this site.</p>
<p>For more information see W3C\'s <a href="http://www.w3.org/TR/html/">HTML Specifications</a> or use your favorite search engine to find other sites that explain HTML.</p>');
							$tips = array(
								'a' => array( t('Anchors are used to make links to other pages.'), '<a href="'. $base_url .'">'. variable_get('site_name', 'Drupal') .'</a>'),
								'br' => array( t('By default line break tags are automatically added, so use this tag to add additional ones. Use of this tag is different because it is not used with an open/close pair like all the others. Use the extra " /" inside the tag to maintain XHTML 1.0 compatibility'), t('Text with <br />line break')),
								'p' => array( t('By default paragraph tags are automatically added, so use this tag to add additional ones.'), '<p>'. t('Paragraph one.') .'</p> <p>'. t('Paragraph two.') .'</p>'),
								'strong' => array( t('Strong'), '<strong>'. t('Strong'). '</strong>'),
								'em' => array( t('Emphasized'), '<em>'. t('Emphasized') .'</em>'),
								'cite' => array( t('Cited'), '<cite>'. t('Cited') .'</cite>'),
								'code' => array( t('Coded text used to show programming source code'), '<code>'. t('Coded') .'</code>'),
								'b' => array( t('Bolded'), '<b>'. t('Bolded') .'</b>'),
								'u' => array( t('Underlined'), '<u>'. t('Underlined') .'</u>'),
								'i' => array( t('Italicized'), '<i>'. t('Italicized') .'</i>'),
								'sup' => array( t('Superscripted'), t('<sup>Super</sup>scripted')),
								'sub' => array( t('Subscripted'), t('<sub>Sub</sub>scripted')),
								'pre' => array( t('Preformatted'), '<pre>'. t('Preformatted') .'</pre>'),
								'abbr' => array( t('Abbreviation'), t('<abbr title="Abbreviation">Abbrev.</abbr>')),
								'acronym' => array( t('Acronym'), t('<acronym title="Three-Letter Acronym">TLA</acronym>')),
								'blockquote' => array( t('Block quoted'), '<blockquote>'. t('Block quoted') .'</blockquote>'),
								'q' => array( t('Quoted inline'), '<q>'. t('Quoted inline') .'</q>'),
								// Assumes and describes tr, td, th.
								'table' => array( t('Table'), '<table> <tr><th>'. t('Table header') .'</th></tr> <tr><td>'. t('Table cell') .'</td></tr> </table>'),
								'tr' => NULL, 'td' => NULL, 'th' => NULL,
								'del' => array( t('Deleted'), '<del>'. t('Deleted') .'</del>'),
								'ins' => array( t('Inserted'), '<ins>'. t('Inserted') .'</ins>'),
								 // Assumes and describes li.
								'ol' => array( t('Ordered list - use the &lt;li&gt; to begin each list item'), '<ol> <li>'. t('First item') .'</li> <li>'. t('Second item') .'</li> </ol>'),
								'ul' => array( t('Unordered list - use the &lt;li&gt; to begin each list item'), '<ul> <li>'. t('First item') .'</li> <li>'. t('Second item') .'</li> </ul>'),
								'li' => NULL,
								// Assumes and describes dt and dd.
								'dl' => array( t('Definition lists are similar to other HTML lists. &lt;dl&gt; begins the definition list, &lt;dt&gt; begins the definition term and &lt;dd&gt; begins the definition description.'), '<dl> <dt>'. t('First term') .'</dt> <dd>'. t('First definition') .'</dd> <dt>'. t('Second term') .'</dt> <dd>'. t('Second definition') .'</dd> </dl>'),
								'dt' => NULL, 'dd' => NULL,
								'h1' => array( t('Header'), '<h1>'. t('Title') .'</h1>'),
								'h2' => array( t('Header'), '<h2>'. t('Subtitle') .'</h2>'),
								'h3' => array( t('Header'), '<h3>'. t('Subtitle three') .'</h3>'),
								'h4' => array( t('Header'), '<h4>'. t('Subtitle four') .'</h4>'),
								'h5' => array( t('Header'), '<h5>'. t('Subtitle five') .'</h5>'),
								'h6' => array( t('Header'), '<h6>'. t('Subtitle six') .'</h6>')
							);
							$header = array(t('Tag Description'), t('You Type'), t('You Get'));
							preg_match_all('/<([a-z0-9]+)[^a-z0-9]/i', $allowed_html, $out);
							foreach ($out[1] as $tag) {
								if (array_key_exists($tag, $tips)) {
									if ($tips[$tag]) {
										$rows[] = array(
											array('data' => $tips[$tag][0], 'class' => 'description'),
											array('data' => '<code>'. check_plain($tips[$tag][1]) .'</code>', 'class' => 'type'),
											array('data' => $tips[$tag][1], 'class' => 'get')
										);
									}
								}
								else {
									$rows[] = array(
										array('data' => t('No help provided for tag %tag.', array('%tag' => $tag)), 'class' => 'description', 'colspan' => 3),
									);
								}
							}
							$output .= theme('table', $header, $rows);

							$output .= t('
<p>Most unusual characters can be directly entered without any problems.</p>
<p>If you do encounter problems, try using HTML character entities. A common example looks like &amp;amp; for an ampersand &amp; character. For a full list of entities see HTML\'s <a href="http://www.w3.org/TR/html4/sgml/entities.html">entities</a> page. Some of the available characters include:</p>');
							$entities = array(
								array( t('Ampersand'), '&amp;'),
								array( t('Greater than'), '&gt;'),
								array( t('Less than'), '&lt;'),
								array( t('Quotation mark'), '&quot;'),
							);
							$header = array(t('Character Description'), t('You Type'), t('You Get'));
							unset($rows);
							foreach ($entities as $entity) {
								$rows[] = array(
									array('data' => $entity[0], 'class' => 'description'),
									array('data' => '<code>'. check_plain($entity[1]) .'</code>', 'class' => 'type'),
									array('data' => $entity[1], 'class' => 'get')
								);
							}
							$output .= theme('table', $header, $rows);
							return $output;
					}
				}
				else {
					return t('No HTML tags allowed');
				}
			}
			break;

		case 1:
			switch ($long) {
				case 0:
					return t('You may post PHP code. You should include &lt;?php ?&gt; tags.');
				case 1:
					return t('
<h4>Using custom PHP code</h4>
<p>If you know how to script in PHP, Drupal gives you the power to embed any script you like. It will be executed when the page is viewed and dynamically embedded into the page. This gives you amazing flexibility and power, but of course with that comes danger and insecurity if you do not write good code. If you are not familiar with PHP, SQL or with the site engine, avoid experimenting with PHP because you can corrupt your database or render your site insecure or even unusable! If you do not plan to do fancy stuff with your content then you are probably better off with straight HTML.</p>
<p>Remember that the code within each PHP item must be valid PHP code - including things like correctly terminating statements with a semicolon. It is highly recommended that you develop your code separately using a simple test script on top of a test database before migrating to your production environment.</p>
<p>Notes:</p><ul><li>You can use global variables, such as configuration parameters, within the scope of your PHP code but remember that global variables which have been given values in your code will retain these values in the engine afterwards.</li><li>register_globals is now set to <strong>off</strong> by default. If you need form information you need to get it from the "superglobals" $_POST, $_GET, etc.</li><li>You can either use the <code>print</code> or <code>return</code> statement to output the actual content for your item.</li></ul>
<p>A basic example:</p>
<blockquote><p>You want to have a box with the title "Welcome" that you use to greet your visitors. The content for this box could be created by going:</p>
<pre>
	print t("Welcome visitor, ... welcome message goes here ...");
</pre>
<p>If we are however dealing with a registered user, we can customize the message by using:</p>
<pre>
	global $user;
	if ($user->uid) {
		print t("Welcome $user->name, ... welcome message goes here ...");
	}
	else {
		print t("Welcome visitor, ... welcome message goes here ...");
	}
</pre></blockquote>
<p>For more in-depth examples, we recommend that you check the existing Drupal code and use it as a starting point, especially for sidebar boxes.</p>');
			}

		case 2:
			switch ($long) {
				case 0:
					return t('Lines and paragraphs break automatically.');
				case 1:
					return t('Lines and paragraphs are automatically recognized. The &lt;br /&gt; line break, &lt;p&gt; paragraph and &lt;/p&gt; close paragraph tags are inserted automatically. If paragraphs are not recognized simply add a couple blank lines.');
			}

		case 3:
			 return t('Web page addresses and e-mail addresses turn into links automatically.');
	}
}

/**
 * Displays a list of all input formats and which one is the default
 */
function filter_admin_overview() {

	// Overview of all formats.
	$formats = filter_formats();
	$error = FALSE;

	foreach ($formats as $id => $format) {
		$roles = array();
		foreach (user_roles() as $rid => $name) {
			// Prepare a roles array with roles that may access the filter
			if (strstr($format->roles, ",$rid,")) {
				$roles[] = $name;
			}
		}
		$default = ($id == variable_get('filter_default_format', 1));
		$options[$id] = '';
		$form[$format->name]['id'] = array('#value' => $id);
		$form[$format->name]['roles'] = array('#value' => $default ? t('All roles may use default format') : ($roles ? implode(', ',$roles) : t('No roles may use this format')));
		$form[$format->name]['configure'] = array('#value' => l(t('configure'), 'admin/settings/filters/'. $id));
		$form[$format->name]['delete'] = array('#value' => $default ? '' : l(t('delete'), 'admin/settings/filters/delete/'. $id));
	}
	$form['default'] = array('#type' => 'radios', '#options' => $options, '#default_value' => variable_get('filter_default_format', 1));
	$form['submit'] = array('#type' => 'submit', '#value' => t('Set default format'));
	return $form;
}

function filter_admin_overview_submit($form_id, $form_values) {
	// Process form submission to set the default format
	if (is_numeric($form_values['default'])) {
		drupal_set_message(t('Default format updated.'));
		variable_set('filter_default_format', $form_values['default']);
	}
}

function theme_filter_admin_overview($form) {
	$rows = array();
	foreach ($form as $name => $element) {
		if (isset($element['roles']) && is_array($element['roles'])) {
			$rows[] = array(
				drupal_render($form['default'][$element['id']['#value']]),
				check_plain($name),
				drupal_render($element['roles']),
				drupal_render($element['configure']),
				drupal_render($element['delete'])
			);
			unset($form[$name]);
		}
	}
	$header = array(t('Default'), t('Name'), t('Roles'), array('data' => t('Operations'), 'colspan' => 2));
	$output = theme('table', $header, $rows);
	$output .= drupal_render($form);

	return $output;
}

/**
 * Menu callback; confirm deletion of a format.
 */
function filter_admin_delete() {
	$format = arg(4);
	$format = db_fetch_object(db_query('SELECT * FROM {filter_formats} WHERE format = %d', $format));

	if ($format) {
		if ($format->format != variable_get('filter_default_format', 1)) {
			$form['format'] = array('#type' => 'hidden', '#value' => $format->format);
			$form['name'] = array('#type' => 'hidden', '#value' => $format->name);

			return confirm_form($form, t('Are you sure you want to delete the input format %format?', array('%format' => $format->name)), 'admin/settings/filters', t('If you have any content left in this input format, it will be switched to the default input format. This action cannot be undone.'), t('Delete'), t('Cancel'));
		}
		else {
			drupal_set_message(t('The default format cannot be deleted.'));
			drupal_goto('admin/settings/filters');
		}
	}
	else {
		drupal_not_found();
	}
}

/**
 * Process filter delete form submission.
 */
function filter_admin_delete_submit($form_id, $form_values) {
	db_query("DELETE FROM {filter_formats} WHERE format = %d", $form_values['format']);
	db_query("DELETE FROM {filters} WHERE format = %d", $form_values['format']);

	$default = variable_get('filter_default_format', 1);
	// Replace existing instances of the deleted format with the default format.
	db_query("UPDATE {node_revisions} SET format = %d WHERE format = %d", $default, $form_values['format']);
	db_query("UPDATE {comments} SET format = %d WHERE format = %d", $default, $form_values['format']);
	db_query("UPDATE {boxes} SET format = %d WHERE format = %d", $default, $form_values['format']);

	cache_clear_all($form_values['format'] .':', 'cache_filter', TRUE);
	drupal_set_message(t('Deleted input format %format.', array('%format' => $form_values['name'])));

	return 'admin/settings/filters';
}

/**
 * Generate a filter format form.
 */
function filter_admin_format_form($format = NULL) {
	$default = ($format->format == variable_get('filter_default_format', 1));
	if ($default) {
		$help = t('All roles for the default format must be enabled and cannot be changed.');
		$form['default_format'] = array('#type' => 'hidden', '#value' => 1);
	}

	$form['name'] = array('#type' => 'textfield',
		'#title' => 'Name',
		'#default_value' => $format->name,
		'#description' => t('Specify a unique name for this filter format.'),
		'#required' => TRUE,
	);

	// Add a row of checkboxes for form group.
	$form['roles'] = array('#type' => 'fieldset',
		'#title' => t('Roles'),
		'#description' => $default ? $help : t('Choose which roles may use this filter format. Note that roles with the "administer filters" permission can always use all the filter formats.'),
		'#tree' => TRUE,
	);

	foreach (user_roles() as $rid => $name) {
		$checked = strstr($format->roles, ",$rid,");
		$form['roles'][$rid] = array('#type' => 'checkbox',
			'#title' => $name,
			'#default_value' => ($default || $checked),
		);
		if ($default) {
			$form['roles'][$rid]['#disabled'] = TRUE;
		}
	}
	// Table with filters
	$all = filter_list_all();
	$enabled = filter_list_format($format->format);

	$form['filters'] = array('#type' => 'fieldset',
		'#title' => t('Filters'),
		'#description' => t('Choose the filters that will be used in this filter format.'),
		'#tree' => TRUE,
	);
	foreach ($all as $id => $filter) {
		$form['filters'][$id] = array('#type' => 'checkbox',
			'#title' => $filter->name,
			'#default_value' => isset($enabled[$id]),
			'#description' => module_invoke($filter->module, 'filter', 'description', $filter->delta),
		);
	}
	if (isset($format)) {
		$form['format'] = array('#type' => 'hidden', '#value' => $format->format);

		// Composition tips (guidelines)
		$tips = _filter_tips($format->format, FALSE);
		$extra = '<p>'. l(t('More information about formatting options'), 'filter/tips') .'</p>';
		$tiplist = theme('filter_tips', $tips, FALSE, $extra);
		if (!$tiplist) {
			$tiplist = '<p>'. t('No guidelines available.') .'</p>';
		}
		$group = '<p>'. t('These are the guidelines that users will see for posting in this input format. They are automatically generated from the filter settings.') .'</p>';
		$group .= $tiplist;
		$form['tips'] = array('#value' => '<h2>'. t('Formatting guidelines') .'</h2>'. $group);
	}
	$form['submit'] = array('#type' => 'submit', '#value' => t('Save configuration'));

	return $form;
}

/**
 * Validate filter format form submissions.
 */
function filter_admin_format_form_validate($form_id, $form_values) {
	if (!isset($form_values['format'])) {
		$name = trim($form_values['name']);
		$result = db_fetch_object(db_query("SELECT format FROM {filter_formats} WHERE name='%s'", $name));
		if ($result) {
			form_set_error('name', t('Filter format names need to be unique. A format named %name already exists.', array('%name' => $name)));
		}
	}
}

/**
 * Process filter format form submissions.
 */
function filter_admin_format_form_submit($form_id, $form_values) {
	$format = isset($form_values['format']) ? $form_values['format'] : NULL;
	$current = filter_list_format($format);
	$name = trim($form_values['name']);
	$cache = TRUE;

	// Add a new filter format.
	if (!$format) {
		$new = TRUE;
		db_query("INSERT INTO {filter_formats} (name) VALUES ('%s')", $name);
		$format = db_result(db_query("SELECT MAX(format) AS format FROM {filter_formats}"));
		drupal_set_message(t('Added input format %format.', array('%format' => $name)));
	}
	else {
		drupal_set_message(t('The input format settings have been updated.'));
	}

	db_query("DELETE FROM {filters} WHERE format = %d", $format);
	foreach ($form_values['filters'] as $id => $checked) {
		if ($checked) {
			list($module, $delta) = explode('/', $id);
			// Add new filters to the bottom.
			$weight = isset($current[$id]->weight) ? $current[$id]->weight : 10;
			db_query("INSERT INTO {filters} (format, module, delta, weight) VALUES (%d, '%s', %d, %d)", $format, $module, $delta, $weight);

			// Check if there are any 'no cache' filters.
			$cache &= !module_invoke($module, 'filter', 'no cache', $delta);
		}
	}

	// We store the roles as a string for ease of use.
	// We should always set all roles to TRUE when saving a default role.
	// We use leading and trailing comma's to allow easy substring matching.
	$roles = array();
	if (isset($form_values['roles'])) {
		foreach ($form_values['roles'] as $id => $checked) {
			if ($checked) {
				$roles[] = $id;
			}
		}
	}
	$roles = ','. implode(',', ($form_values['default_format'] ? array_keys(user_roles()) : $roles)) .',';

	db_query("UPDATE {filter_formats} SET cache = %d, name='%s', roles = '%s' WHERE format = %d", $cache, $name, $roles, $format);

	cache_clear_all($format .':', 'cache_filter', TRUE);

	// If a new filter was added, return to the main list of filters. Otherwise, stay on edit filter page to show new changes.
	if ($new) {
		return 'admin/settings/filters/';
	}
	else {
		return 'admin/settings/filters/'. $format;
	}
}

/**
 * Menu callback; display form for ordering filters for a format.
 */
function filter_admin_order($format = NULL) {
	// Get list (with forced refresh)
	$filters = filter_list_format($format->format);

	$form['weights'] = array('#tree' => TRUE);
	foreach ($filters as $id => $filter) {
		$form['names'][$id] = array('#value' => $filter->name);
		$form['weights'][$id] = array('#type' => 'weight', '#default_value' => $filter->weight);
	}
	$form['format'] = array('#type' => 'hidden', '#value' => $format->format);
	$form['submit'] = array('#type' => 'submit', '#value' => t('Save configuration'));

	return $form;
}

/**
 * Theme filter order configuration form.
 */
function theme_filter_admin_order($form) {
	$header = array(t('Name'), t('Weight'));
	$rows = array();
	foreach (element_children($form['names']) as $id) {
		// Don't take form control structures
		if (is_array($form['names'][$id])) {
			$rows[] = array(drupal_render($form['names'][$id]), drupal_render($form['weights'][$id]));
		}
	}

	$output = theme('table', $header, $rows);
	$output .= drupal_render($form);

	return $output;
}

/**
 * Process filter order configuration form submission.
 */
function filter_admin_order_submit($form_id, $form_values) {
	foreach ($form_values['weights'] as $id => $weight) {
		list($module, $delta) = explode('/', $id);
		db_query("UPDATE {filters} SET weight = %d WHERE format = %d AND module = '%s' AND delta = %d", $weight, $form_values['format'], $module, $delta);
	}
	drupal_set_message(t('The filter ordering has been saved.'));

	cache_clear_all($form_values['format'] .':', 'cache_filter', TRUE);
}

/**
 * Menu callback; display settings defined by filters.
 */
function filter_admin_configure() {
	$format = arg(3);

	$list = filter_list_format($format);
	$form = array();
	foreach ($list as $filter) {
		$form_module = module_invoke($filter->module, 'filter', 'settings', $filter->delta, $format);
		if (isset($form_module) && is_array($form_module)) {
			$form = array_merge($form, $form_module);
		}
	}

	if (!empty($form)) {
		$form = system_settings_form($form);
		$form['format'] = array('#type' => 'hidden', '#value' => $format);
		$form['#submit']['system_settings_form_submit'] = array();
		$form['#submit']['filter_admin_configure_submit'] = array();
	}
	else {
		$form['error'] = array('#value' => t('No settings are available.'));
	}

	return $form;
}

/**
 * Clear the filter's cache when configuration settings are saved.
 */
function filter_admin_configure_submit($form_id, $form_values) {
	cache_clear_all($form_values['format'] .':', 'cache_filter', TRUE);
}

/**
 * Retrieve a list of input formats.
 */
function filter_formats() {
	global $user;
	static $formats;

	// Administrators can always use all input formats.
	$all = user_access('administer filters');

	if (!isset($formats)) {
		$formats = array();

		$query = 'SELECT * FROM {filter_formats}';

		// Build query for selecting the format(s) based on the user's roles.
		$args = array();
		if (!$all) {
			$where = array();
			foreach ($user->roles as $rid => $role) {
				$where[] = "roles LIKE '%%,%d,%%'";
				$args[] = $rid;
			}
			$query .= ' WHERE '. implode(' OR ', $where) . ' OR format = %d';
			$args[] = variable_get('filter_default_format', 1);
		}

		$result = db_query($query, $args);
		while ($format = db_fetch_object($result)) {
			$formats[$format->format] = $format;
		}
	}
	return $formats;
}

/**
 * Build a list of all filters.
 */
function filter_list_all() {
	$filters = array();

	foreach (module_list() as $module) {
		$list = module_invoke($module, 'filter', 'list');
		if (isset($list) && is_array($list)) {
			foreach ($list as $delta => $name) {
				$filters[$module .'/'. $delta] = (object)array('module' => $module, 'delta' => $delta, 'name' => $name);
			}
		}
	}

	uasort($filters, '_filter_list_cmp');

	return $filters;
}

/**
 * Helper function for sorting the filter list by filter name.
 */
function _filter_list_cmp($a, $b) {
	return strcmp($a->name, $b->name);
}

/**
 * Resolve a format id, including the default format.
 */
function filter_resolve_format($format) {
	return $format == FILTER_FORMAT_DEFAULT ? variable_get('filter_default_format', 1) : $format;
}
/**
 * Check if text in a certain input format is allowed to be cached.
 */
function filter_format_allowcache($format) {
	static $cache = array();
	$format = filter_resolve_format($format);
	if (!isset($cache[$format])) {
		$cache[$format] = db_result(db_query('SELECT cache FROM {filter_formats} WHERE format = %d', $format));
	}
	return $cache[$format];
}

/**
 * Retrieve a list of filters for a certain format.
 */
function filter_list_format($format) {
	static $filters = array();

	if (!isset($filters[$format])) {
		$result = db_query("SELECT * FROM {filters} WHERE format = %d ORDER BY weight ASC", $format);
		if (db_num_rows($result) == 0 && !db_result(db_query("SELECT 1 FROM {filter_formats} WHERE format = %d", $format))) {
			// The format has no filters and does not exist, use the default input
			// format.
			$filters[$format] = filter_list_format(variable_get('filter_default_format', 1));
		}
		else {
			$filters[$format] = array();
			while ($filter = db_fetch_object($result)) {
				$list = module_invoke($filter->module, 'filter', 'list');
				if (isset($list) && is_array($list) && isset($list[$filter->delta])) {
					$filter->name = $list[$filter->delta];
					$filters[$format][$filter->module .'/'. $filter->delta] = $filter;
				}
			}
		}
	}

	return $filters[$format];
}

/**
 * @name Filtering functions
 * @{
 * Modules which need to have content filtered can use these functions to
 * interact with the filter system.
 *
 * For more info, see the hook_filter() documentation.
 *
 * Note: because filters can inject JavaScript or execute PHP code, security is
 * vital here. When a user supplies a $format, you should validate it with
 * filter_access($format) before accepting/using it. This is normally done in
 * the validation stage of the node system. You should for example never make a
 * preview of content in a disallowed format.
 */

/**
 * Run all the enabled filters on a piece of text.
 *
 * @param $text
 *    The text to be filtered.
 * @param $format
 *    The format of the text to be filtered. Specify FILTER_FORMAT_DEFAULT for
 *    the default format.
 * @param $check
 *    Whether to check the $format with filter_access() first. Defaults to TRUE.
 *    Note that this will check the permissions of the current user, so you
 *    should specify $check = FALSE when viewing other people's content. When
 *    showing content that is not (yet) stored in the database (eg. upon preview),
 *    set to TRUE so the user's permissions are checked.
 */
function check_markup($text, $format = FILTER_FORMAT_DEFAULT, $check = TRUE) {
	// When $check = TRUE, do an access check on $format.
	if (isset($text) && (!$check || filter_access($format))) {
		$format = filter_resolve_format($format);

		// Check for a cached version of this piece of text.
		$id = $format .':'. md5($text);
		if ($cached = cache_get($id, 'cache_filter')) {
			return $cached->data;
		}

		// See if caching is allowed for this format.
		$cache = filter_format_allowcache($format);

		// Convert all Windows and Mac newlines to a single newline,
		// so filters only need to deal with one possibility.
		$text = str_replace(array("\r\n", "\r"), "\n", $text);

		// Get a complete list of filters, ordered properly.
		$filters = filter_list_format($format);

		// Give filters the chance to escape HTML-like data such as code or formulas.
		foreach ($filters as $filter) {
			$text = module_invoke($filter->module, 'filter', 'prepare', $filter->delta, $format, $text);
		}

		// Perform filtering.
		foreach ($filters as $filter) {
			$text = module_invoke($filter->module, 'filter', 'process', $filter->delta, $format, $text);
		}

		// Store in cache with a minimum expiration time of 1 day.
		if ($cache) {
			cache_set($id, 'cache_filter', $text, time() + (60 * 60 * 24));
		}
	}
	else {
		$text = t('n/a');
	}

	return $text;
}

/**
 * Generate a selector for choosing a format in a form.
 *
 * @param $value
 *   The ID of the format that is currently selected.
 * @param $weight
 *   The weight of the input format.
 * @param $parents
 *   Required when defining multiple input formats on a single node or having a different parent than 'format'.
 * @return
 *   HTML for the form element.
 */
function filter_form($value = FILTER_FORMAT_DEFAULT, $weight = NULL, $parents = array('format')) {
	$value = filter_resolve_format($value);
	$formats = filter_formats();

	$extra = theme('filter_tips_more_info');

	if (count($formats) > 1) {
		$form = array(
			'#type' => 'fieldset',
			'#title' => t('Input format'),
			'#collapsible' => TRUE,
			'#collapsed' => TRUE,
			'#weight' => $weight,
			'#validate' => array('filter_form_validate' => array()),
		);
		// Multiple formats available: display radio buttons with tips.
		foreach ($formats as $format) {
			$form[$format->format] = array(
				'#type' => 'radio',
				'#title' => $format->name,
				'#default_value' => $value,
				'#return_value' => $format->format,
				'#parents' => $parents,
				'#description' => theme('filter_tips', _filter_tips($format->format, FALSE)),
			);
		}
	}
	else {
		// Only one format available: use a hidden form item and only show tips.
		$format = array_shift($formats);
		$form[$format->format] = array('#type' => 'value', '#value' => $format->format, '#parents' => $parents);
		$tips = _filter_tips(variable_get('filter_default_format', 1), FALSE);
		$form['format']['guidelines'] = array(
			'#title' => t('Formatting guidelines'),
			'#value' => theme('filter_tips', $tips, FALSE, $extra),
		);
	}
	$form[] = array('#value' => $extra);
	return $form;
}

function filter_form_validate($form) {
	foreach (element_children($form) as $key) {
		if ($form[$key]['#value'] == $form[$key]['#return_value']) {
			return;
		}
	}
	form_error($form, t('An illegal choice has been detected. Please contact the site administrator.'));
	watchdog('form', t('Illegal choice %choice in %name element.', array('%choice' => $form[$key]['#value'], '%name' => empty($form['#title']) ? $form['#parents'][0] : $form['#title'])), WATCHDOG_ERROR);
}

/**
 * Returns TRUE if the user is allowed to access this format.
 */
function filter_access($format) {
	$format = filter_resolve_format($format);
	if (user_access('administer filters') || ($format == variable_get('filter_default_format', 1))) {
		return TRUE;
	}
	else {
		$formats = filter_formats();
		return isset($formats[$format]);
	}
}
/**
 * @} End of "Filtering functions".
 */

/**
 * Menu callback; show a page with long filter tips.
 */
function filter_tips_long() {
	$format = arg(2);
	if ($format) {
		$output = theme('filter_tips', _filter_tips($format, TRUE), TRUE);
	}
	else {
		$output = theme('filter_tips', _filter_tips(-1, TRUE), TRUE);
	}
	return $output;
}

/**
 * Helper function for fetching filter tips.
 */
function _filter_tips($format, $long = FALSE) {
	if ($format == -1) {
		$formats = filter_formats();
	}
	else {
		$formats = array(db_fetch_object(db_query("SELECT * FROM {filter_formats} WHERE format = %d", $format)));
	}

	$tips = array();

	foreach ($formats as $format) {
		$filters = filter_list_format($format->format);

		$tips[$format->name] = array();
		foreach ($filters as $id => $filter) {
			if ($tip = module_invoke($filter->module, 'filter_tips', $filter->delta, $format->format, $long)) {
				$tips[$format->name][] = array('tip' => $tip, 'id' => $id);
			}
		}
	}

	return $tips;
}

/**
 * Format a set of filter tips.
 *
 * @ingroup themeable
 */
function theme_filter_tips($tips, $long = FALSE, $extra = '') {
	$output = '';

	$multiple = count($tips) > 1;
	if ($multiple) {
		$output = t('input formats') .':';
	}

	if (count($tips)) {
		if ($multiple) {
			$output .= '<ul>';
		}
		foreach ($tips as $name => $tiplist) {
			if ($multiple) {
				$output .= '<li>';
				$output .= '<strong>'. $name .'</strong>:<br />';
			}

			if (count($tiplist) > 0) {
				$output .= '<ul class="tips">';
				foreach ($tiplist as $tip) {
					$output .= '<li'. ($long ? ' id="filter-'. str_replace("/", "-", $tip['id']) .'">' : '>') . $tip['tip'] .'</li>';
				}
				$output .= '</ul>';
			}

			if ($multiple) {
				$output .= '</li>';
			}
		}
		if ($multiple) {
			$output .= '</ul>';
		}
	}

	return $output;
}

/**
 * Format a link to the more extensive filter tips.
 *
 * @ingroup themeable
 */

function theme_filter_tips_more_info() {
	return '<p>'. l(t('More information about formatting options'), 'filter/tips') .'</p>';
}

/**
 * @name Standard filters
 * @{
 * Filters implemented by the filter.module.
 */

/**
 * Implementation of hook_filter(). Contains a basic set of essential filters.
 * - HTML filter:
 *     Validates user-supplied HTML, transforming it as necessary.
 * - PHP evaluator:
 *     Executes PHP code.
 * - Line break converter:
 *     Converts newlines into paragraph and break tags.
 */
function filter_filter($op, $delta = 0, $format = -1, $text = '') {
	switch ($op) {
		case 'list':
			return array(0 => t('HTML filter'), 1 => t('PHP evaluator'), 2 => t('Line break converter'), 3 => t('URL filter'));

		case 'no cache':
			return $delta == 1; // No caching for the PHP evaluator.

		case 'description':
			switch ($delta) {
				case 0:
					return t('Allows you to restrict if users can post HTML and which tags to filter out.');
				case 1:
					return t('Runs a piece of PHP code. The usage of this filter should be restricted to administrators only!');
				case 2:
					return t('Converts line breaks into HTML (i.e. &lt;br&gt; and &lt;p&gt; tags).');
				case 3:
					return t('Turns web and e-mail addresses into clickable links.');
				default:
					return;
			}

		case 'process':
			switch ($delta) {
				case 0:
					return _filter_html($text, $format);
				case 1:
					return drupal_eval($text);
				case 2:
					return _filter_autop($text);
				case 3:
					return _filter_url($text, $format);
				default:
					return $text;
			}

		case 'settings':
			switch ($delta) {
				case 0:
					return _filter_html_settings($format);
				case 3:
					return _filter_url_settings($format);
				default:
					return;
			}

		default:
			return $text;
	}
}

/**
 * Settings for the HTML filter.
 */
function _filter_html_settings($format) {
	$form['filter_html'] = array(
		'#type' => 'fieldset',
		'#title' => t('HTML filter'),
		'#collapsible' => TRUE,
	);
	$form['filter_html']["filter_html_$format"] = array(
		'#type' => 'radios',
		'#title' => t('Filter HTML tags'),
		'#default_value' => variable_get("filter_html_$format", FILTER_HTML_STRIP),
		'#options' => array(FILTER_HTML_STRIP => t('Strip disallowed tags'), FILTER_HTML_ESCAPE => t('Escape all tags')),
		'#description' => t('How to deal with HTML tags in user-contributed content. If set to "Strip disallowed tags", dangerous tags are removed (see below). If set to "Escape tags", all HTML is escaped and presented as it was typed.'),
	);
	$form['filter_html']["allowed_html_$format"] = array(
		'#type' => 'textfield',
		'#title' => t('Allowed HTML tags'),
		'#default_value' => variable_get("allowed_html_$format", '<a> <em> <strong> <cite> <code> <ul> <ol> <li> <dl> <dt> <dd>'),
		'#size' => 64,
		'#maxlength' => 1024,
		'#description' => t('If "Strip disallowed tags" is selected, optionally specify tags which should not be stripped. JavaScript event attributes are always stripped.'),
	);
	$form['filter_html']["filter_html_help_$format"] = array(
		'#type' => 'checkbox',
		'#title' => t('Display HTML help'),
		'#default_value' => variable_get("filter_html_help_$format", 1),
		'#description' => t('If enabled, Drupal will display some basic HTML help in the long filter tips.'),
	);
	$form['filter_html']["filter_html_nofollow_$format"] = array(
		'#type' => 'checkbox',
		'#title' => t('Spam link deterrent'),
		'#default_value' => variable_get("filter_html_nofollow_$format", FALSE),
		'#description' => t('If enabled, Drupal will add rel="nofollow" to all links, as a measure to reduce the effectiveness of spam links. Note: this will also prevent valid links from being followed by search engines, therefore it is likely most effective when enabled for anonymous users.'),
	);
	return $form;
}

/**
 * HTML filter. Provides filtering of input into accepted HTML.
 */
function _filter_html($text, $format) {
	if (variable_get("filter_html_$format", FILTER_HTML_STRIP) == FILTER_HTML_STRIP) {
		$allowed_tags = preg_split('/\s+|<|>/', variable_get("allowed_html_$format", '<a> <em> <strong> <cite> <code> <ul> <ol> <li> <dl> <dt> <dd>'), -1, PREG_SPLIT_NO_EMPTY);
		$text = filter_xss($text, $allowed_tags);
	}

	if (variable_get("filter_html_$format", FILTER_HTML_STRIP) == FILTER_HTML_ESCAPE) {
		// Escape HTML
		$text = check_plain($text);
	}

	if (variable_get("filter_html_nofollow_$format", FALSE)) {
		$text = preg_replace('/<a([^>]+)>/i', '<a\\1 rel="nofollow">', $text);
	}

	return trim($text);
}

/**
 * Settings for URL filter.
 */
function _filter_url_settings($format) {
	$form['filter_urlfilter'] = array(
		'#type' => 'fieldset',
		'#title' => t('URL filter'),
		'#collapsible' => TRUE,
	);
	$form['filter_urlfilter']['filter_url_length_'. $format] = array(
		'#type' => 'textfield',
		'#title' => t('Maximum link text length'),
		'#default_value' => variable_get('filter_url_length_'. $format, 72),
		'#maxlength' => 4,
		'#description' => t('URLs longer than this number of characters will be truncated to prevent long strings that break formatting. The link itself will be retained; just the text portion of the link will be truncated.'),
	);
	return $form;
}

/**
 * URL filter. Automatically converts text web addresses (URLs, e-mail addresses,
 * ftp links, etc.) into hyperlinks.
 */
function _filter_url($text, $format) {
	// Pass length to regexp callback
	_filter_url_trim(NULL, variable_get('filter_url_length_'. $format, 72));

	$text   = ' '. $text .' ';

	// Match absolute URLs.
	$text = preg_replace_callback("`(<p>|<li>|<br\s*/?>|[ \n\r\t\(])((http://|https://|ftp://|mailto:|smb://|afp://|file://|gopher://|news://|ssl://|sslv2://|sslv3://|tls://|tcp://|udp://)([a-zA-Z0-9@:%_+*~#?&=.,/;-]*[a-zA-Z0-9@:%_+*~#&=/;-]))([.,?!]*?)(?=(</p>|</li>|<br\s*/?>|[ \n\r\t\)]))`i", '_filter_url_parse_full_links', $text);

	// Match e-mail addresses.
	$text = preg_replace("`(<p>|<li>|<br\s*/?>|[ \n\r\t\(])([A-Za-z0-9._-]+@[A-Za-z0-9._+-]+\.[A-Za-z]{2,4})([.,?!]*?)(?=(</p>|</li>|<br\s*/?>|[ \n\r\t\)]))`i", '\1<a href="mailto:\2">\2</a>\3', $text);

	// Match www domains/addresses.
	$text = preg_replace_callback("`(<p>|<li>|[ \n\r\t\(])(www\.[a-zA-Z0-9@:%_+*~#?&=.,/;-]*[a-zA-Z0-9@:%_+~#\&=/;-])([.,?!]*?)(?=(</p>|</li>|<br\s*/?>|[ \n\r\t\)]))`i", '_filter_url_parse_partial_links', $text);
	$text = substr($text, 1, -1);

	return $text;
}

/**
 * Make links out of absolute URLs.
 */
function _filter_url_parse_full_links($match) {
	$match[2] = decode_entities($match[2]);
	$caption = check_plain(_filter_url_trim($match[2]));
	$match[2] = check_url($match[2]);
	return $match[1] . '<a href="'. $match[2] .'" title="'. $match[2] .'">'. $caption .'</a>'. $match[5];
}

/**
 * Make links out of domain names starting with "www."
 */
function _filter_url_parse_partial_links($match) {
	$match[2] = decode_entities($match[2]);
	$caption = check_plain(_filter_url_trim($match[2]));
	$match[2] = check_plain($match[2]);
	return $match[1] . '<a href="http://'. $match[2] .'" title="'. $match[2] .'">'. $caption .'</a>'. $match[3];
}

/**
 * Shortens long URLs to http://www.example.com/long/url...
 */
function _filter_url_trim($text, $length = NULL) {
	static $_length;
	if ($length !== NULL) {
		$_length = $length;
	}

	if (strlen($text) > $_length) {
		$text = substr($text, 0, $_length) .'...';
	}

	return $text;
}

/**
 * Convert line breaks into <p> and <br> in an intelligent fashion.
 * Based on: http://photomatt.net/scripts/autop
 */
function _filter_autop($text) {
	// All block level tags
	$block = '(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|p|h[1-6]|hr)';

	// Split at <pre>, <script>, <style> and </pre>, </script>, </style> tags.
	// We don't apply any processing to the contents of these tags to avoid messing
	// up code. We look for matched pairs and allow basic nesting. For example:
	// "processed <pre> ignored <script> ignored </script> ignored </pre> processed"
	$chunks = preg_split('@(</?(?:pre|script|style|object)[^>]*>)@i', $text, -1, PREG_SPLIT_DELIM_CAPTURE);
	// Note: PHP ensures the array consists of alternating delimiters and literals
	// and begins and ends with a literal (inserting NULL as required).
	$ignore = FALSE;
	$ignoretag = '';
	$output = '';
	foreach ($chunks as $i => $chunk) {
		if ($i % 2) {
			// Opening or closing tag?
			$open = ($chunk[1] != '/');
			list($tag) = split('[ >]', substr($chunk, 2 - $open), 2);
			if (!$ignore) {
				if ($open) {
					$ignore = TRUE;
					$ignoretag = $tag;
				}
			}
			// Only allow a matching tag to close it.
			else if (!$open && $ignoretag == $tag) {
				$ignore = FALSE;
				$ignoretag = '';
			}
		}
		else if (!$ignore) {
			$chunk = preg_replace('|\n*$|', '', $chunk) ."\n\n"; // just to make things a little easier, pad the end
			$chunk = preg_replace('|<br />\s*<br />|', "\n\n", $chunk);
			$chunk = preg_replace('!(<'. $block .'[^>]*>)!', "\n$1", $chunk); // Space things out a little
			$chunk = preg_replace('!(</'. $block .'>)!', "$1\n\n", $chunk); // Space things out a little
			$chunk = preg_replace("/\n\n+/", "\n\n", $chunk); // take care of duplicates
			$chunk = preg_replace('/\n?(.+?)(?:\n\s*\n|\z)/s', "<p>$1</p>\n", $chunk); // make paragraphs, including one at the end
			$chunk = preg_replace('|<p>\s*</p>\n|', '', $chunk); // under certain strange conditions it could create a P of entirely whitespace
			$chunk = preg_replace("|<p>(<li.+?)</p>|", "$1", $chunk); // problem with nested lists
			$chunk = preg_replace('|<p><blockquote([^>]*)>|i', "<blockquote$1><p>", $chunk);
			$chunk = str_replace('</blockquote></p>', '</p></blockquote>', $chunk);
			$chunk = preg_replace('!<p>\s*(</?'. $block .'[^>]*>)!', "$1", $chunk);
			$chunk = preg_replace('!(</?'. $block .'[^>]*>)\s*</p>!', "$1", $chunk);
			$chunk = preg_replace('|(?<!<br />)\s*\n|', "<br />\n", $chunk); // make line breaks
			$chunk = preg_replace('!(</?'. $block .'[^>]*>)\s*<br />!', "$1", $chunk);
			$chunk = preg_replace('!<br />(\s*</?(?:p|li|div|th|pre|td|ul|ol)>)!', '$1', $chunk);
			$chunk = preg_replace('/&([^#])(?![A-Za-z0-9]{1,8};)/', '&amp;$1', $chunk);
		}
		$output .= $chunk;
	}
	return $output;
}

/**
 * Very permissive XSS/HTML filter for admin-only use.
 *
 * Use only for fields where it is impractical to use the
 * whole filter system, but where some (mainly inline) mark-up
 * is desired (so check_plain() is not acceptable).
 *
 * Allows all tags that can be used inside an HTML body, save
 * for scripts and styles.
 */
function filter_xss_admin($string) {
	return filter_xss($string, array('a', 'abbr', 'acronym', 'address', 'b', 'bdo', 'big', 'blockquote', 'br', 'caption', 'cite', 'code', 'col', 'colgroup', 'dd', 'del', 'dfn', 'div', 'dl', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins', 'kbd', 'li', 'ol', 'p', 'pre', 'q', 'samp', 'small', 'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'tt', 'ul', 'var'));
}

/**
 * Filters XSS. Based on kses by Ulf Harnhammar, see
 * http://sourceforge.net/projects/kses
 *
 * For examples of various XSS attacks, see:
 * http://ha.ckers.org/xss.html
 *
 * This code does four things:
 * - Removes characters and constructs that can trick browsers
 * - Makes sure all HTML entities are well-formed
 * - Makes sure all HTML tags and attributes are well-formed
 * - Makes sure no HTML tags contain URLs with a disallowed protocol (e.g. javascript:)
 *
 * @param $string
 *   The string with raw HTML in it. It will be stripped of everything that can cause
 *   an XSS attack.
 * @param $allowed_tags
 *   An array of allowed tags.
 * @param $format
 *   The format to use.
 */
function filter_xss($string, $allowed_tags = array('a', 'em', 'strong', 'cite', 'code', 'ul', 'ol', 'li', 'dl', 'dt', 'dd')) {
	// Store the input format
	_filter_xss_split($allowed_tags, TRUE);
	// Remove NUL characters (ignored by some browsers)
	$string = str_replace(chr(0), '', $string);
	// Remove Netscape 4 JS entities
	$string = preg_replace('%&\s*\{[^}]*(\}\s*;?|$)%', '', $string);

	// Defuse all HTML entities
	$string = str_replace('&', '&amp;', $string);
	// Change back only well-formed entities in our whitelist
	// Named entities
	$string = preg_replace('/&amp;([A-Za-z][A-Za-z0-9]*;)/', '&\1', $string);
	// Decimal numeric entities
	$string = preg_replace('/&amp;#([0-9]+;)/', '&#\1', $string);
	// Hexadecimal numeric entities
	$string = preg_replace('/&amp;#[Xx]0*((?:[0-9A-Fa-f]{2})+;)/', '&#x\1', $string);

	return preg_replace_callback('%
		(
		<(?=[^a-zA-Z!/])  # a lone <
		|                 # or
		<[^>]*(>|$)       # a string that starts with a <, up until the > or the end of the string
		|                 # or
		>                 # just a >
		)%x', '_filter_xss_split', $string);
}

/**
 * Processes an HTML tag.
 *
 * @param @m
 *   An array with various meaning depending on the value of $store.
 *   If $store is TRUE then the array contains the allowed tags.
 *   If $store is FALSE then the array has one element, the HTML tag to process.
 * @param $store
 *   Whether to store $m.
 * @return
 *   If the element isn't allowed, an empty string. Otherwise, the cleaned up
 *   version of the HTML element.
 */
function _filter_xss_split($m, $store = FALSE) {
	static $allowed_html;

	if ($store) {
		$allowed_html = array_flip($m);
		return;
	}

	$string = $m[1];

	if (substr($string, 0, 1) != '<') {
		// We matched a lone ">" character
		return '&gt;';
	}
	else if (strlen($string) == 1) {
		// We matched a lone "<" character
		return '&lt;';
	}

	if (!preg_match('%^<\s*(/\s*)?([a-zA-Z0-9]+)([^>]*)>?$%', $string, $matches)) {
		// Seriously malformed
		return '';
	}

	$slash = trim($matches[1]);
	$elem = &$matches[2];
	$attrlist = &$matches[3];

	if (!isset($allowed_html[strtolower($elem)])) {
		// Disallowed HTML element
		return '';
	}

	if ($slash != '') {
		return "</$elem>";
	}

	// Is there a closing XHTML slash at the end of the attributes?
	// In PHP 5.1.0+ we could count the changes, currently we need a separate match
	$xhtml_slash = preg_match('%\s?/\s*$%', $attrlist) ? ' /' : '';
	$attrlist = preg_replace('%(\s?)/\s*$%', '\1', $attrlist);

	// Clean up attributes
	$attr2 = implode(' ', _filter_xss_attributes($attrlist));
	$attr2 = preg_replace('/[<>]/', '', $attr2);
	$attr2 = strlen($attr2) ? ' '. $attr2 : '';

	return "<$elem$attr2$xhtml_slash>";
}

/**
 * Processes a string of HTML attributes.
 *
 * @return
 *   Cleaned up version of the HTML attributes.
 */
function _filter_xss_attributes($attr) {
	$attrarr = array();
	$mode = 0;
	$attrname = '';

	while (strlen($attr) != 0) {
		// Was the last operation successful?
		$working = 0;

		switch ($mode) {
			case 0:
				// Attribute name, href for instance
				if (preg_match('/^([-a-zA-Z]+)/', $attr, $match)) {
					$attrname = strtolower($match[1]);
					$skip = ($attrname == 'style' || substr($attrname, 0, 2) == 'on');
					$working = $mode = 1;
					$attr = preg_replace('/^[-a-zA-Z]+/', '', $attr);
				}

				break;

			case 1:
				// Equals sign or valueless ("selected")
				if (preg_match('/^\s*=\s*/', $attr)) {
					$working = 1; $mode = 2;
					$attr = preg_replace('/^\s*=\s*/', '', $attr);
					break;
				}

				if (preg_match('/^\s+/', $attr)) {
					$working = 1; $mode = 0;
					if (!$skip) {
						$attrarr[] = $attrname;
					}
					$attr = preg_replace('/^\s+/', '', $attr);
				}

				break;

			case 2:
				// Attribute value, a URL after href= for instance
				if (preg_match('/^"([^"]*)"(\s+|$)/', $attr, $match)) {
					$thisval = filter_xss_bad_protocol($match[1]);

					if (!$skip) {
						$attrarr[] = "$attrname=\"$thisval\"";
					}
					$working = 1;
					$mode = 0;
					$attr = preg_replace('/^"[^"]*"(\s+|$)/', '', $attr);
					break;
				}

				if (preg_match("/^'([^']*)'(\s+|$)/", $attr, $match)) {
					$thisval = filter_xss_bad_protocol($match[1]);

					if (!$skip) {
						$attrarr[] = "$attrname='$thisval'";;
					}
					$working = 1; $mode = 0;
					$attr = preg_replace("/^'[^']*'(\s+|$)/", '', $attr);
					break;
				}

				if (preg_match("%^([^\s\"']+)(\s+|$)%", $attr, $match)) {
					$thisval = filter_xss_bad_protocol($match[1]);

					if (!$skip) {
						$attrarr[] = "$attrname=\"$thisval\"";
					}
					$working = 1; $mode = 0;
					$attr = preg_replace("%^[^\s\"']+(\s+|$)%", '', $attr);
				}

				break;
		}

		if ($working == 0) {
			// not well formed, remove and try again
			$attr = preg_replace('/
				^
				(
				"[^"]*("|$)     # - a string that starts with a double quote, up until the next double quote or the end of the string
				|               # or
				\'[^\']*(\'|$)| # - a string that starts with a quote, up until the next quote or the end of the string
				|               # or
				\S              # - a non-whitespace character
				)*              # any number of the above three
				\s*             # any number of whitespaces
				/x', '', $attr);
			$mode = 0;
		}
	}

	// the attribute list ends with a valueless attribute like "selected"
	if ($mode == 1) {
		$attrarr[] = $attrname;
	}
	return $attrarr;
}

/**
 * Processes an HTML attribute value and ensures it does not contain an URL
 * with a disallowed protocol (e.g. javascript:)
 *
 * @param $string
 *   The string with the attribute value.
 * @param $decode
 *   Whether to decode entities in the $string. Set to FALSE if the $string
 *   is in plain text, TRUE otherwise. Defaults to TRUE.
 * @return
 *   Cleaned up and HTML-escaped version of $string.
 */
function filter_xss_bad_protocol($string, $decode = TRUE) {
	static $allowed_protocols;
	if (!isset($allowed_protocols)) {
		$allowed_protocols = array_flip(variable_get('filter_allowed_protocols', array('http', 'https', 'ftp', 'news', 'nntp', 'telnet', 'mailto', 'irc', 'ssh', 'sftp', 'webcal')));
	}

	// Get the plain text representation of the attribute value (i.e. its meaning).
	if ($decode) {
		$string = decode_entities($string);
	}

	// Iteratively remove any invalid protocol found.

	do {
		$before = $string;
		$colonpos = strpos($string, ':');
		if ($colonpos > 0) {
			// We found a colon, possibly a protocol. Verify.
			$protocol = substr($string, 0, $colonpos);
			// If a colon is preceded by a slash, question mark or hash, it cannot
			// possibly be part of the URL scheme. This must be a relative URL,
			// which inherits the (safe) protocol of the base document.
			if (preg_match('![/?#]!', $protocol)) {
				break;
			}
			// Per RFC2616, section 3.2.3 (URI Comparison) scheme comparison must be case-insensitive.
			// Check if this is a disallowed protocol.
			if (!isset($allowed_protocols[strtolower($protocol)])) {
				$string = substr($string, $colonpos + 1);
			}
		}
	} while ($before != $string);
	return check_plain($string);
}

echo filter_filter($argv[1], $argv[2], $argv[3], file_get_contents("php://stdin"));

?>

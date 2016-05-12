<?php

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

function drupal_validate_utf8($text) {
  if (strlen($text) == 0) {
    return TRUE;
  }
  // For performance reasons this logic is duplicated in check_plain().
  return (preg_match('/^./us', $text) == 1);
}

function check_plain($text) {
  static $php525;

  if (!isset($php525)) {
    $php525 = version_compare(PHP_VERSION, '5.2.5', '>=');
  }

  if ($php525) {
    return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
  }
  return (preg_match('/^./us', $text) == 1) ? htmlspecialchars($text, ENT_QUOTES, 'UTF-8') : '';
}


/**
 * @defgroup filtering_functions Filtering functions
 * @{
 * Functions for interacting with the content filtering system.
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
 * Generates a selector for choosing a format in a form.
 *
 * @param $value
 *   The ID of the format that is currently selected; uses the default format
 *   if not provided.
 * @param $weight
 *   The weight of the form element within the form.
 * @param $parents
 *   The parents array of the element. Required when defining multiple text
 *   formats on a single form or having a different parent than 'format'.
 *
 * @return
 *   Form API array for the form element.
 *
 * @see filter_form_validate()
 * @ingroup forms
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
      '#element_validate' => array('filter_form_validate'),
    );
    // Multiple formats available: display radio buttons with tips.
    foreach ($formats as $format) {
      // Generate the parents as the autogenerator does, so we will have a
      // unique id for each radio button.
      $parents_for_id = array_merge($parents, array($format->format));
      $form[$format->format] = array(
        '#type' => 'radio',
        '#title' => $format->name,
        '#default_value' => $value,
        '#return_value' => $format->format,
        '#parents' => $parents,
        '#description' => theme('filter_tips', _filter_tips($format->format, FALSE)),
        '#id' => form_clean_id('edit-'. implode('-', $parents_for_id)),
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

/**
 * Validation callback for filter elements in a form.
 *
 * @see filter_form().
 */
function filter_form_validate($form) {
  foreach (element_children($form) as $key) {
    if ($form[$key]['#value'] == $form[$key]['#return_value']) {
      return;
    }
  }
  form_error($form, t('An illegal choice has been detected. Please contact the site administrator.'));
  watchdog('form', 'Illegal choice %choice in %name element.', array('%choice' => $form[$key]['#value'], '%name' => empty($form['#title']) ? $form['#parents'][0] : $form['#title']), WATCHDOG_ERROR);
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
 * Format a link to the more extensive filter tips.
 *
 * @ingroup themeable
 */
function theme_filter_tips_more_info() {
  return '<p>'. l(t('More information about formatting options'), 'filter/tips') .'</p>';
}

/**
 * @defgroup standard_filters Standard filters
 * @{
 * Filters implemented by the filter.module.
 */

/**
 * Implementation of hook_filter().
 *
 * Sets up a basic set of essential filters.
 * - HTML filter: Restricts user-supplied HTML to certain tags, and removes
 *   dangerous components in allowed tags.
 * - Line break converter: Converts newlines into paragraph and break tags.
 * - URL filter: Converts URLs and e-mail addresses into links.
 * - HTML corrector: Fixes faulty HTML.
 */
function filter_filter($op, $delta = 0, $format = -1, $text = '') {
  switch ($op) {
    case 'list':
      return array(0 => t('HTML filter'), 1 => t('Line break converter'), 2 => t('URL filter'), 3 => t('HTML corrector'));

    case 'description':
      switch ($delta) {
        case 0:
          return t('Allows you to restrict whether users can post HTML and which tags to filter out. It will also remove harmful content such as JavaScript events, JavaScript URLs and CSS styles from those tags that are not removed.');
        case 1:
          return t('Converts line breaks into HTML (i.e. &lt;br&gt; and &lt;p&gt; tags).');
        case 2:
          return t('Turns web and e-mail addresses into clickable links.');
        case 3:
          return t('Corrects faulty and chopped off HTML in postings.');
        default:
          return;
      }

    case 'process':
      switch ($delta) {
        case 0:
          return _filter_html($text, $format);
        case 1:
          return _filter_autop($text);
        case 2:
          return _filter_url($text, $format);
        case 3:
          return _filter_htmlcorrector($text);
        default:
          return $text;
      }

    case 'settings':
      switch ($delta) {
        case 0:
          return _filter_html_settings($format);
        case 2:
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
  $allowed_tags = preg_split('/\s+|<|>/', '<a> <em> <strong> <cite> <code> <ul> <ol> <li> <dl> <dt> <dd>', -1, PREG_SPLIT_NO_EMPTY);
  $text = filter_xss($text, $allowed_tags);

  $text = check_plain($text);

  if (FALSE) {
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
 * FTP links, etc.) into hyperlinks.
 */
function _filter_url($text, $format) {
  // Pass length to regexp callback
  _filter_url_trim(NULL, variable_get('filter_url_length_'. $format, 72));

  $text = ' '. $text .' ';

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
 * Scan input and make sure that all HTML tags are properly closed and nested.
 */
function _filter_htmlcorrector($text) {
  // Prepare tag lists.
  static $no_nesting, $single_use;
  if (!isset($no_nesting)) {
    // Tags which cannot be nested but are typically left unclosed.
    $no_nesting = drupal_map_assoc(array('li', 'p'));

    // Single use tags in HTML4
    $single_use = drupal_map_assoc(array('base', 'meta', 'link', 'hr', 'br', 'param', 'img', 'area', 'input', 'col', 'frame'));
  }

  // Properly entify angles.
  $text = preg_replace('@<(?=[^a-zA-Z!/]|$)@', '&lt;', $text);

  // Split tags from text.
  $split = preg_split('/<(!--.*?--|[^>]+?)>/s', $text, -1, PREG_SPLIT_DELIM_CAPTURE);
  // Note: PHP ensures the array consists of alternating delimiters and literals
  // and begins and ends with a literal (inserting $null as required).

  $tag = false; // Odd/even counter. Tag or no tag.
  $stack = array();
  $output = '';
  foreach ($split as $value) {
    // Process HTML tags.
    if ($tag) {
      // Passthrough comments.
      if (substr($value, 0, 3) == '!--') {
        $output .= '<'. $value .'>';
      }
      else {
        list($tagname) = preg_split('/\s/', strtolower($value), 2);
        // Closing tag
        if ($tagname{0} == '/') {
          $tagname = substr($tagname, 1);
          // Discard XHTML closing tags for single use tags.
          if (!isset($single_use[$tagname])) {
            // See if we possibly have a matching opening tag on the stack.
            if (in_array($tagname, $stack)) {
              // Close other tags lingering first.
              do {
                $output .= '</'. $stack[0] .'>';
              } while (array_shift($stack) != $tagname);
            }
            // Otherwise, discard it.
          }
        }
        // Opening tag
        else {
          // See if we have an identical 'no nesting' tag already open and close it if found.
          if (count($stack) && ($stack[0] == $tagname) && isset($no_nesting[$stack[0]])) {
            $output .= '</'. array_shift($stack) .'>';
          }
          // Push non-single-use tags onto the stack
          if (!isset($single_use[$tagname])) {
            array_unshift($stack, $tagname);
          }
          // Add trailing slash to single-use tags as per X(HT)ML.
          else {
            $value = rtrim($value, ' /') .' /';
          }
          $output .= '<'. $value .'>';
        }
      }
    }
    else {
      // Passthrough all text.
      $output .= $value;
    }
    $tag = !$tag;
  }
  // Close remaining tags.
  while (count($stack) > 0) {
    $output .= '</'. array_shift($stack) .'>';
  }
  return $output;
}

/**
 * Make links out of absolute URLs.
 */
function _filter_url_parse_full_links($match) {
  $match[2] = decode_entities($match[2]);
  $caption = check_plain(_filter_url_trim($match[2]));
  $match[2] = check_url($match[2]);
  return $match[1] .'<a href="'. $match[2] .'" title="'. $match[2] .'">'. $caption .'</a>'. $match[5];
}

/**
 * Make links out of domain names starting with "www."
 */
function _filter_url_parse_partial_links($match) {
  $match[2] = decode_entities($match[2]);
  $caption = check_plain(_filter_url_trim($match[2]));
  $match[2] = check_plain($match[2]);
  return $match[1] .'<a href="http://'. $match[2] .'" title="'. $match[2] .'">'. $caption .'</a>'. $match[3];
}

/**
 * Shortens long URLs to http://www.example.com/long/url...
 */
function _filter_url_trim($text, $length = NULL) {
  static $_length;
  if ($length !== NULL) {
    $_length = $length;
  }

  // Use +3 for '...' string length.
  if (strlen($text) > $_length + 3) {
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
  $chunks = preg_split('@(<(?:!--.*?--|/?(?:pre|script|style|object)[^>]*)>)@si', $text, -1, PREG_SPLIT_DELIM_CAPTURE);
  // Note: PHP ensures the array consists of alternating delimiters and literals
  // and begins and ends with a literal (inserting NULL as required).
  $ignore = FALSE;
  $ignoretag = '';
  $output = '';
  foreach ($chunks as $i => $chunk) {
    if ($i % 2) {
      // Passthrough comments.
      if (substr($chunk, 1, 3) == '!--') {
        $output .= $chunk;
      }
      else {
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
    }
    else if (!$ignore) {
      $chunk = preg_replace('|\n*$|', '', $chunk) ."\n\n"; // just to make things a little easier, pad the end
      $chunk = preg_replace('|<br />\s*<br />|', "\n\n", $chunk);
      $chunk = preg_replace('!(<'. $block .'[^>]*>)!', "\n$1", $chunk); // Space things out a little
      $chunk = preg_replace('!(</'. $block .'>)!', "$1\n\n", $chunk); // Space things out a little
      $chunk = preg_replace("/\n\n+/", "\n\n", $chunk); // take care of duplicates
      $chunk = preg_replace('/^\n|\n\s*\n$/', '', $chunk);
      $chunk = '<p>'. preg_replace('/\n\s*\n\n?(.)/', "</p>\n<p>$1", $chunk) ."</p>\n"; // make paragraphs, including one at the end
      $chunk = preg_replace("|<p>(<li.+?)</p>|", "$1", $chunk); // problem with nested lists
      $chunk = preg_replace('|<p><blockquote([^>]*)>|i', "<blockquote$1><p>", $chunk);
      $chunk = str_replace('</blockquote></p>', '</p></blockquote>', $chunk);
      $chunk = preg_replace('|<p>\s*</p>\n?|', '', $chunk); // under certain strange conditions it could create a P of entirely whitespace
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
 * Filters an HTML string to prevent cross-site-scripting (XSS) vulnerabilities.
 *
 * Based on kses by Ulf Harnhammar, see http://sourceforge.net/projects/kses.
 * For examples of various XSS attacks, see http://ha.ckers.org/xss.html.
 *
 * This code does four things:
 * - Removes characters and constructs that can trick browsers.
 * - Makes sure all HTML entities are well-formed.
 * - Makes sure all HTML tags and attributes are well-formed.
 * - Makes sure no HTML tags contain URLs with a disallowed protocol (e.g.
 *   javascript:).
 *
 * @param $string
 *   The string with raw HTML in it. It will be stripped of everything that can
 *   cause an XSS attack.
 * @param $allowed_tags
 *   An array of allowed tags.
 *
 * @return
 *   An XSS safe version of $string, or an empty string if $string is not
 *   valid UTF-8.
 *
 * @see drupal_validate_utf8()
 * @ingroup sanitization
 */
function filter_xss($string, $allowed_tags = array('a', 'em', 'strong', 'cite', 'code', 'ul', 'ol', 'li', 'dl', 'dt', 'dd')) {
  // Only operate on valid UTF-8 strings. This is necessary to prevent cross
  // site scripting issues on Internet Explorer 6.
  if (!drupal_validate_utf8($string)) {
    return '';
  }
  // Store the input format
  _filter_xss_split($allowed_tags, TRUE);
  // Remove NUL characters (ignored by some browsers)
  $string = str_replace(chr(0), '', $string);
  // Remove Netscape 4 JS entities
  $string = preg_replace('%&\s*\{[^}]*(\}\s*;?|$)%', '', $string);

  // Defuse all HTML entities
  $string = str_replace('&', '&amp;', $string);
  // Change back only well-formed entities in our whitelist
  // Decimal numeric entities
  $string = preg_replace('/&amp;#([0-9]+;)/', '&#\1', $string);
  // Hexadecimal numeric entities
  $string = preg_replace('/&amp;#[Xx]0*((?:[0-9A-Fa-f]{2})+;)/', '&#x\1', $string);
  // Named entities
  $string = preg_replace('/&amp;([A-Za-z][A-Za-z0-9]*;)/', '&\1', $string);

  return preg_replace_callback('%
    (
    <(?=[^a-zA-Z!/])  # a lone <
    |                 # or
    <!--.*?-->        # a comment
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

  if (!preg_match('%^(?:<\s*(/\s*)?([a-zA-Z0-9]+)([^>]*)>?|(<!--.*?-->))$%', $string, $matches)) {
    // Seriously malformed
    return '';
  }

  $slash = trim($matches[1]);
  $elem = &$matches[2];
  $attrlist = &$matches[3];
  $comment = &$matches[4];

  if ($comment) {
    $elem = '!--';
  }

  if (!isset($allowed_html[strtolower($elem)])) {
    // Disallowed HTML element
    return '';
  }

  if ($comment) {
    return $comment;
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

echo filter_filter('process', 0, 'Filtered HTML', 'input');

/**
 * @} End of "Standard filters".
 */

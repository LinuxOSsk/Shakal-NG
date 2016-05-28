<?php

error_reporting(E_ERROR);

define('FILTER_FORMAT_DEFAULT', 0);

define('FILTER_HTML_STRIP', 1);
define('FILTER_HTML_ESCAPE', 2);

function variable_init() {
	return array("filter_default_format" => "1");
}

$conf = variable_init();

function variable_get($name, $default) {
	global $conf;
	return isset($conf[$name]) ? $conf[$name] : $default;
}

function drupal_validate_utf8($text) {
	if (strlen($text) == 0) {
		return TRUE;
	}
	return (preg_match('/^./us', $text) == 1);
}

function _decode_entities($prefix, $codepoint, $original, &$table, &$exclude) {
	// Named entity
	if (!$prefix) {
		if (isset($table[$original])) {
			return $table[$original];
		}
		else {
			return $original;
		}
	}
	// Hexadecimal numerical entity
	if ($prefix == '#x') {
		$codepoint = base_convert($codepoint, 16, 10);
	}
	// Decimal numerical entity (strip leading zeros to avoid PHP octal notation)
	else {
		$codepoint = preg_replace('/^0+/', '', $codepoint);
	}
	// Encode codepoint as UTF-8 bytes
	if ($codepoint < 0x80) {
		$str = chr($codepoint);
	}
	else if ($codepoint < 0x800) {
		$str = chr(0xC0 | ($codepoint >> 6))
				 . chr(0x80 | ($codepoint & 0x3F));
	}
	else if ($codepoint < 0x10000) {
		$str = chr(0xE0 | ( $codepoint >> 12))
				 . chr(0x80 | (($codepoint >> 6) & 0x3F))
				 . chr(0x80 | ( $codepoint       & 0x3F));
	}
	else if ($codepoint < 0x200000) {
		$str = chr(0xF0 | ( $codepoint >> 18))
				 . chr(0x80 | (($codepoint >> 12) & 0x3F))
				 . chr(0x80 | (($codepoint >> 6)  & 0x3F))
				 . chr(0x80 | ( $codepoint        & 0x3F));
	}
	// Check for excluded characters
	if (in_array($str, $exclude)) {
		return $original;
	}
	else {
		return $str;
	}
}

function decode_entities($text, $exclude = array()) {
	static $table;
	// We store named entities in a table for quick processing.
	if (!isset($table)) {
		// Get all named HTML entities.
		$table = array_flip(get_html_translation_table(HTML_ENTITIES));
		// PHP gives us ISO-8859-1 data, we need UTF-8.
		$table = array_map('utf8_encode', $table);
		// Add apostrophe (XML)
		$table['&apos;'] = "'";
	}
	$newtable = array_diff($table, $exclude);

	// Use a regexp to select all entities in one pass, to avoid decoding double-escaped entities twice.
	return preg_replace('/&(#x?)?([A-Za-z0-9]+);/e', '_decode_entities("$1", "$2", "$0", $newtable, $exclude)', $text);
}

function check_plain($text) {
	return drupal_validate_utf8($text) ? htmlspecialchars($text, ENT_QUOTES) : '';
}

function check_url($uri) {
	return filter_xss_bad_protocol($uri, FALSE);
}

function drupal_eval($code) {
	ob_start();
	print eval('?>'. $code);
	$output = ob_get_contents();
	ob_end_clean();
	return $output;
}

?>

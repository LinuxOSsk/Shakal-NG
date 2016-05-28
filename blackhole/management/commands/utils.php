<?php

error_reporting(E_ERROR);

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

function drupal_map_assoc($array, $function = NULL) {
	if (!isset($function)) {
		$result = array();
		foreach ($array as $value) {
			$result[$value] = $value;
		}
		return $result;
	}
	elseif (function_exists($function)) {
		$result = array();
		foreach ($array as $value) {
			$result[$value] = $function($value);
		}
		return $result;
	}
}

function variable_init() {
	return array("filter_default_format" => "1");
}

$conf = variable_init();

function variable_get($name, $default) {
	global $conf;
	return isset($conf[$name]) ? $conf[$name] : $default;
}



$html_entities = array(
	'&Aacute;' => 'Á',
	'&aacute;' => 'á',
	'&Acirc;' => 'Â',
	'&acirc;' => 'â',
	'&acute;' => '´',
	'&AElig;' => 'Æ',
	'&aelig;' => 'æ',
	'&Agrave;' => 'À',
	'&agrave;' => 'à',
	'&alefsym;' => 'ℵ',
	'&Alpha;' => 'Α',
	'&alpha;' => 'α',
	'&amp;' => '&',
	'&and;' => '∧',
	'&ang;' => '∠',
	'&Aring;' => 'Å',
	'&aring;' => 'å',
	'&asymp;' => '≈',
	'&Atilde;' => 'Ã',
	'&atilde;' => 'ã',
	'&Auml;' => 'Ä',
	'&auml;' => 'ä',
	'&bdquo;' => '„',
	'&Beta;' => 'Β',
	'&beta;' => 'β',
	'&brvbar;' => '¦',
	'&bull;' => '•',
	'&cap;' => '∩',
	'&Ccedil;' => 'Ç',
	'&ccedil;' => 'ç',
	'&cedil;' => '¸',
	'&cent;' => '¢',
	'&Chi;' => 'Χ',
	'&chi;' => 'χ',
	'&circ;' => 'ˆ',
	'&clubs;' => '♣',
	'&cong;' => '≅',
	'&copy;' => '©',
	'&crarr;' => '↵',
	'&cup;' => '∪',
	'&curren;' => '¤',
	'&dagger;' => '†',
	'&Dagger;' => '‡',
	'&darr;' => '↓',
	'&dArr;' => '⇓',
	'&deg;' => '°',
	'&Delta;' => 'Δ',
	'&delta;' => 'δ',
	'&diams;' => '♦',
	'&divide;' => '÷',
	'&Eacute;' => 'É',
	'&eacute;' => 'é',
	'&Ecirc;' => 'Ê',
	'&ecirc;' => 'ê',
	'&Egrave;' => 'È',
	'&egrave;' => 'è',
	'&empty;' => '∅',
	'&emsp;' => ' ',
	'&ensp;' => ' ',
	'&Epsilon;' => 'Ε',
	'&epsilon;' => 'ε',
	'&equiv;' => '≡',
	'&Eta;' => 'Η',
	'&eta;' => 'η',
	'&ETH;' => 'Ð',
	'&eth;' => 'ð',
	'&Euml;' => 'Ë',
	'&euml;' => 'ë',
	'&euro;' => '€',
	'&exist;' => '∃',
	'&fnof;' => 'ƒ',
	'&forall;' => '∀',
	'&frac12;' => '½',
	'&frac14;' => '¼',
	'&frac34;' => '¾',
	'&frasl;' => '⁄',
	'&Gamma;' => 'Γ',
	'&gamma;' => 'γ',
	'&ge;' => '≥',
	'&harr;' => '↔',
	'&hArr;' => '⇔',
	'&hearts;' => '♥',
	'&hellip;' => '…',
	'&Iacute;' => 'Í',
	'&iacute;' => 'í',
	'&Icirc;' => 'Î',
	'&icirc;' => 'î',
	'&iexcl;' => '¡',
	'&Igrave;' => 'Ì',
	'&igrave;' => 'ì',
	'&image;' => 'ℑ',
	'&infin;' => '∞',
	'&int;' => '∫',
	'&Iota;' => 'Ι',
	'&iota;' => 'ι',
	'&iquest;' => '¿',
	'&isin;' => '∈',
	'&Iuml;' => 'Ï',
	'&iuml;' => 'ï',
	'&Kappa;' => 'Κ',
	'&kappa;' => 'κ',
	'&Lambda;' => 'Λ',
	'&lambda;' => 'λ',
	'&lang;' => '〈',
	'&laquo;' => '«',
	'&larr;' => '←',
	'&lArr;' => '⇐',
	'&lceil;' => '⌈',
	'&ldquo;' => '“',
	'&le;' => '≤',
	'&lfloor;' => '⌊',
	'&lowast;' => '∗',
	'&loz;' => '◊',
	'&lrm;' => '‎',
	'&lsaquo;' => '‹',
	'&lsquo;' => '‘',
	'&macr;' => '¯',
	'&mdash;' => '—',
	'&micro;' => 'µ',
	'&middot;' => '·',
	'&minus;' => '−',
	'&Mu;' => 'Μ',
	'&mu;' => 'μ',
	'&nabla;' => '∇',
	'&nbsp;' => ' ',
	'&ndash;' => '–',
	'&ne;' => '≠',
	'&ni;' => '∋',
	'&not;' => '¬',
	'&notin;' => '∉',
	'&nsub;' => '⊄',
	'&Ntilde;' => 'Ñ',
	'&ntilde;' => 'ñ',
	'&Nu;' => 'Ν',
	'&nu;' => 'ν',
	'&Oacute;' => 'Ó',
	'&oacute;' => 'ó',
	'&Ocirc;' => 'Ô',
	'&ocirc;' => 'ô',
	'&OElig;' => 'Œ',
	'&oelig;' => 'œ',
	'&Ograve;' => 'Ò',
	'&ograve;' => 'ò',
	'&oline;' => '‾',
	'&Omega;' => 'Ω',
	'&omega;' => 'ω',
	'&Omicron;' => 'Ο',
	'&omicron;' => 'ο',
	'&oplus;' => '⊕',
	'&or;' => '∨',
	'&ordf;' => 'ª',
	'&ordm;' => 'º',
	'&Oslash;' => 'Ø',
	'&oslash;' => 'ø',
	'&Otilde;' => 'Õ',
	'&otilde;' => 'õ',
	'&otimes;' => '⊗',
	'&Ouml;' => 'Ö',
	'&ouml;' => 'ö',
	'&para;' => '¶',
	'&part;' => '∂',
	'&permil;' => '‰',
	'&perp;' => '⊥',
	'&Phi;' => 'Φ',
	'&phi;' => 'φ',
	'&Pi;' => 'Π',
	'&pi;' => 'π',
	'&piv;' => 'ϖ',
	'&plusmn;' => '±',
	'&pound;' => '£',
	'&prime;' => '′',
	'&Prime;' => '″',
	'&prod;' => '∏',
	'&prop;' => '∝',
	'&Psi;' => 'Ψ',
	'&psi;' => 'ψ',
	'&radic;' => '√',
	'&rang;' => '〉',
	'&raquo;' => '»',
	'&rarr;' => '→',
	'&rArr;' => '⇒',
	'&rceil;' => '⌉',
	'&rdquo;' => '”',
	'&real;' => 'ℜ',
	'&reg;' => '®',
	'&rfloor;' => '⌋',
	'&Rho;' => 'Ρ',
	'&rho;' => 'ρ',
	'&rlm;' => '‏',
	'&rsaquo;' => '›',
	'&rsquo;' => '’',
	'&sbquo;' => '‚',
	'&Scaron;' => 'Š',
	'&scaron;' => 'š',
	'&sdot;' => '⋅',
	'&sect;' => '§',
	'&shy;' => '­',
	'&Sigma;' => 'Σ',
	'&sigma;' => 'σ',
	'&sigmaf;' => 'ς',
	'&sim;' => '∼',
	'&spades;' => '♠',
	'&sub;' => '⊂',
	'&sube;' => '⊆',
	'&sum;' => '∑',
	'&sup1;' => '¹',
	'&sup2;' => '²',
	'&sup3;' => '³',
	'&sup;' => '⊃',
	'&supe;' => '⊇',
	'&szlig;' => 'ß',
	'&Tau;' => 'Τ',
	'&tau;' => 'τ',
	'&there4;' => '∴',
	'&Theta;' => 'Θ',
	'&theta;' => 'θ',
	'&thetasym;' => 'ϑ',
	'&thinsp;' => ' ',
	'&THORN;' => 'Þ',
	'&thorn;' => 'þ',
	'&tilde;' => '˜',
	'&times;' => '×',
	'&trade;' => '™',
	'&Uacute;' => 'Ú',
	'&uacute;' => 'ú',
	'&uarr;' => '↑',
	'&uArr;' => '⇑',
	'&Ucirc;' => 'Û',
	'&ucirc;' => 'û',
	'&Ugrave;' => 'Ù',
	'&ugrave;' => 'ù',
	'&uml;' => '¨',
	'&upsih;' => 'ϒ',
	'&Upsilon;' => 'Υ',
	'&upsilon;' => 'υ',
	'&Uuml;' => 'Ü',
	'&uuml;' => 'ü',
	'&weierp;' => '℘',
	'&Xi;' => 'Ξ',
	'&xi;' => 'ξ',
	'&Yacute;' => 'Ý',
	'&yacute;' => 'ý',
	'&yen;' => '¥',
	'&yuml;' => 'ÿ',
	'&Yuml;' => 'Ÿ',
	'&Zeta;' => 'Ζ',
	'&zeta;' => 'ζ',
	'&zwj;' => '‍',
	'&zwnj;' => '‌',
	'&gt;' => '>',
	'&lt;' => '<',
	'&quot;' => '"',
	// Add apostrophe (XML).
	'&apos;' => "'",
);


function _decode_entities($prefix, $codepoint, $original, &$html_entities, &$exclude) {
	// Named entity
	if (!$prefix) {
		// A named entity not in the exclude list.
		if (isset($html_entities[$original]) && !isset($exclude[$html_entities[$original]])) {
			return $html_entities[$original];
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
	if (isset($exclude[$str])) {
		return $original;
	}
	else {
		return $str;
	}
}



function decode_entities($text, $exclude = array()) {
	$exclude = array_flip($exclude);

	return preg_replace('/&(#x?)?([A-Za-z0-9]+);/e', '_decode_entities("$1", "$2", "$0", $html_entities, $exclude)', $text);
}



?>

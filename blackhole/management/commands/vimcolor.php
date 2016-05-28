<?php

require "utils.php";


function vimcolor_process_color($text,$type) {
	$multiline = ereg("[\n\r]", $text);
	// Note, pay attention to odd preg_replace-with-/e behaviour on slashes
	// Undo possible linebreak filter conversion
	$text = preg_replace('@</?(br|p)\s*/?>@', '', str_replace('\"', '"', $text));
	// Undo the escaping in the prepare step
	$text = decode_entities($text);
	// Trim leading and trailing linebreaks
	$text = trim($text, "\r\n");
	$text = preg_replace('/\r\n/s', "\n", $text);
	$text = preg_replace('/\r/s', '', $text);
	// Highlight as Code
	$in_file = tempnam('/tmp', 'pl');
	$out_file = tempnam('/tmp', 'htm');
	$handle = fopen($in_file, "w");
		fwrite($handle, $text);
	fclose($handle);
	if($type){
		$type = '--filetype '.$type;
	}
	system('/usr/bin/text-vimcolor --format html '.$type.' '.$in_file.' --output '.$out_file);
	$handle = fopen($out_file, "r");
		$html = fread($handle, filesize($out_file));
	fclose($handle);
	if( $multiline ){
		$html = preg_replace('/\r/s','',$html);
		$html = preg_replace('/\n/s','<br />',$html);
		$html = '<div class="codeblock"><code>'. $html .'</code></div>';
		$html = preg_replace('/  /s','&nbsp; ',$html);
	}else{
		$html = '<code>'. trim($html) .'</code>';
	}
	return $html;
}

function vimcolor_fix_indent($text) {
	return str_replace(' ', '&nbsp;', $text[0]);
}

function vimcolor_escape($text) {
	// Note, pay attention to odd preg_replace-with-/e behaviour on slashes
	return check_plain(str_replace('\"', '"', $text));
}

function vimcolor_filter($op, $delta = 0, $format = -1, $text = '') {
	switch ($op) {
		case 'list':
			return array(0 => t('Code filter'));

		case 'description':
			return t('Allows users to post code verbatim using &lt;code&gt;, &lt;code type="language"&gt;, and &lt;?php ?&gt; tags.');

		case 'prepare':
			// Note: we use the bytes 0xFE and 0xFF to replace < > during the filtering process.
			// These bytes are not valid in UTF-8 data and thus least likely to cause problems.
			$text = preg_replace('@<code( type="([a-z]+)")?>(.*?)</code>@se', "'\xFEcode_start:\\2\xFF'. vimcolor_escape('\\3') .'\xFE/code_end\xFF'", $text);
			$text = preg_replace('@[\[<](\?php|%)(.+?)(\?|%)[\]>]@se', "'\xFEcode_start:php\xFF'. vimcolor_escape('<?php \\2 ?>') .'\xFE/code_end\xFF'", $text);
			return $text;

		case "process":
			$text = preg_replace('@\xFEcode_start:([a-z]*)\xFF(.+?)\xFE/code_end\xFF@se', "vimcolor_process_color('$2','$1')", $text);
			return $text;

		default:
			return $text;
	}
}

echo vimcolor_filter($argv[1], $argv[2], $argv[3], file_get_contents("php://stdin"));
//echo vimcolor_filter('process', $argv[1], $argv[2], file_get_contents("php://stdin"));

?>

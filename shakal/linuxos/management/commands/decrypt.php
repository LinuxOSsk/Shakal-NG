<?php

$user = $argv[1];
$password = $argv[2];
$host = $argv[3];
$dbname = $argv[5];
$key = $argv[6];

include 'Crypt_Xtea-1.1.0/Xtea.php';

mysql_connect($host, $user, $password);
mysql_select_db($dbname);
mysql_query('SET NAMES utf8');

$crypt = new Crypt_Xtea();

$result = mysql_query('SELECT id, heslo FROM users');
$i = 0;
while ($row = mysql_fetch_assoc($result)) {
	$decoded = $crypt->decrypt((string)base64_decode($row["heslo"]), $key);
	$i++;
	echo $i . "\r";
	if (!mysql_query('UPDATE users SET heslo = "' . mysql_real_escape_string($decoded) . '" WHERE id = ' . $row["id"])) {
		echo mysql_error();
	}
}

?>

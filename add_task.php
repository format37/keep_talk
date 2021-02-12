<?php
header('Content-Type: text/html; charset=utf-8');
function Query($query)
{
	$host	= "localhost";	
	$user	= "client";
	$pwd	= "password";
	$dbase	= "gpt2";
	$answerLine	= "";
	$answer= array();
	$link = mysqli_connect($host, $user, $pwd, $dbase);
	//var_dump($link);
	if (mysqli_connect_errno()) {
	    exit();
		//echo 'mysqli_connect_errno';
	}
	if (mysqli_multi_query($link, $query)) {
		//echo 'query ok';
	    do {
	        if ($result = mysqli_store_result($link)) {
	            while ($row = mysqli_fetch_row($result)) {
					$answer[]=$row;
	            }
	            mysqli_free_result($result);
	        }
	        if (mysqli_more_results($link)) {
	        	;
	        }
	    } while (mysqli_more_results($link)&&mysqli_next_result($link));
	}
	mysqli_close($link);
	return $answer;
}
//clear last result
//$fd = fopen("logs/predictions_SortaBig.txt", 'w') or die("unable to cleear file");
//fwrite($fd, '');
//fclose($fd);
$date=date("Y-m-d H:i:s");
$chat=$_GET['chat'];
$source=$_GET['source'];
$message_id=$_GET['message_id'];
$query="SET NAMES utf8;INSERT INTO requests (created, chat, message_id, source) VALUES ('{$date}', '{$chat}', '{$message_id}', '{$source}');";
//echo $query;
$result= Query($query);
//var_dump($result);
?>
<?php
function Query($query)
{
	$host	= "localhost";
	$user	= "user";
	$pwd	= "xxx";
	$dbase	= "mysql";
	$answerLine	= "";
	$answer= array();
	$link = mysqli_connect($host, $user, $pwd, $dbase);
	if (mysqli_connect_errno()) {
	    exit();
	}
	if (mysqli_multi_query($link, $query)) {
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
$date=date("Y-m-d H:i:s");
$chat=$_GET['chat'];
$source=$_GET['source'];
$query="INSERT INTO requests (created, chat, source) VALUES ('{$date}', '{$chat}', '{$source}');";
$result= Query($query);
var_dump($result);
echo '<br>'.$query;
?>
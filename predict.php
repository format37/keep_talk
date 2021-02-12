<?php
//cd /etc/apache2/
//sudo nano apache2.conf
//User pi
//Group pi
//sudo visudo
//www-data ALL=(ALL) NOPASSWD: ALL
//http://95.165.139.53/gpt2robot/predict.php?cmd="That%20was%20a%20sad%20story."

/*
$f=fopen('logs/predictions_SortaBig.txt','w');
fwrite($f,'');
fclose($f);
$command = 'python3 main.py --model PrettyBig.json --top_k 40 --predict_text '.$_GET['cmd'].' 2>&1';
echo('s<br>');
$pid = popen( $command,"r");
while( !feof( $pid ) )
{
         echo fread($pid, 256);
         flush();
         ob_flush();
         usleep(100000);
}
pclose($pid);
echo('<br>r');
$result=file_get_contents('logs/predictions_SortaBig.txt');
$answer	= file_get_contents('http://scriptlab.net/telegram/bots/relaybot/relaylocked.php?chat=106129214&text='.$result);
echo('<br>k: '.$answer);
*/
?>
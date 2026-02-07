## TASK:  Combine the attacks you have learned in this module to obtain the flag. 
the first thing I saw was the application screen with the login panel :
---
<img width="1023" height="430" alt="obraz" src="https://github.com/user-attachments/assets/e34b40ab-38de-4da1-bdb0-d74112a06f87" /><br>  
I immediately saw the option to create a new user, so I did so with the password requirements:<br>  
---
<img width="978" height="191" alt="obraz" src="https://github.com/user-attachments/assets/d9251f2c-6355-4dac-8276-2438ae2db57a" /><br>  
After logging in, I was redirected to /profile.php, which didn't pique my interest at first.<br>  
---
<img width="210" height="34" alt="obraz" src="https://github.com/user-attachments/assets/18ae5712-779b-4de3-9a68-301199eb796f" /><br>  
I brute-forced the username because I noticed that the application responded differently when I entered an existing name regardless of the password<br>  
Invalid credentials Or Unknown username or password.<br> 
I got the login and I also managed to brute force the password using the rockyou.txt list, matching it to the password format<br>  
and I got a screen with an OTP code:<br>  
<img width="999" height="277" alt="obraz" src="https://github.com/user-attachments/assets/031a2f43-e626-4789-9b36-07868a03e31c" /><br>  
---
I tried to brute force the OTP code but it didn't help so I went back to looking around the application<br>  
I went back to the user and remembered that you can force the application to show the page by changing the response code<br>  
---
<img width="690" height="77" alt="obraz" src="https://github.com/user-attachments/assets/d9b8a1fe-cfdc-4f37-b77c-cba222de5962" /><br>  
this is what we need to change and we get a flag :)<br>  
---
<img width="356" height="152" alt="obraz" src="https://github.com/user-attachments/assets/acc8a2bd-1553-4440-86d2-34faae1d696b" /><br>  







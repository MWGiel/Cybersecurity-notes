The HTTP protocol works by accepting various HTTP methods as verbs at the beginning of an HTTP request. Depending on the web server configuration, web applications may be scripted to accept certain HTTP methods for their various functionalities and perform a particular action based on the type of the request.

While programmers mainly consider the two most commonly used HTTP methods, GET and POST, any client can send any other methods in their HTTP requests and then see how the web server handles these methods. Suppose both the web application and the back-end web server are configured only to accept GET and POST requests. In that case, sending a different request will cause a web server error page to be displayed, which is not a severe vulnerability in itself (other than providing a bad user experience and potentially leading to information disclosure). On the other hand, if the web server configurations are not restricted to only accept the HTTP methods required by the web server (e.g. GET/POST), and the web application is not developed to handle other types of HTTP requests (e.g. HEAD, PUT), then we may be able to exploit this insecure configuration to gain access to functionalities we do not have access to, or even bypass certain security controls.
## HTTP Verb Tampering
To understand HTTP Verb Tampering, we must first learn about the different methods accepted by the HTTP protocol. HTTP has 9 different verbs that can be accepted as HTTP methods by web servers. Other than GET and POST, the following are some of the commonly used HTTP verbs:
- HEAD 	Identical to a GET request, but its response only contains the headers, without the response body
- PUT 	Writes the request payload to the specified location
- DELETE 	Deletes the resource at the specified location
- OPTIONS 	Shows different options accepted by a web server, like accepted HTTP verbs
- PATCH 	Apply partial modifications to the resource at the specified location

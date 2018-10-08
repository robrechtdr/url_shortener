# Url Shortener

## Problem description

Your primary task is to build a URL shortener web service using Java, Scala or Python.

### Requirements

Your web service should have a POST /shorten_url endpoint that receives a JSON body with the URL to shorten. A successful request will return a JSON body with the shortened url. If a GET request is made to the shortened URL then the user should be redirected to the the original URL, or returned the contents of the original URL.

It should perform appropriate validation on the URL to be shortened, and return appropriate error responses if the URL is not valid.
It should contain a README.md file with instructions on how to run your service.

> This task is simple and straightforward, so we will be assessing you on your implementation of web services, use of the language and solid engineering practices. Use this as an opportunity to demonstrate how you write code and solve problems. 

> You should also build your web service so it can scale to a thousands of requests per second. Please explain in your README.md file how does your solution allow for it and how would you scale it.

### Example usage:

1. `GET www.helloworld.com -> hello world`

2.     

   ```    
	Request:

	  POST www.your_service.com/shorten_url

	  body:

	  {

	  "url": "www.helloworld.com"

	  }

	Response:

	  Status code: 201

	  response_body:

	  {

	  "shortened_url": 'http://www.your_service.com/ouoYFY48'

	  }
   ```


3. `GET http://www.your_service.com/ouoYFY48 -> hello world`


## Solution

### Installation

> Have virtualenv and virtualenvwrapper installed.

	mkvirtualenv url_shortener
	pip install -r requirements.txt

Also create postgres user `me` with pw `pw` and db `mydb`.


### Running

#### Run server

> `-w n`: with `n` being (#cores of machine x 2) + 1.

	gunicorn -w 9 url_shortener_service:app

#### Generate a shortened url from a full url

	curl -v --header "Content-Type: application/json" --request POST --data '{"url":"www.helloworld.com"}' http://localhost:5000/shorten_url


#### Get redirected to full url given shortened url

> -v shows status code returned. The url hash will be different for you as randomly generated.

	curl http://localhost:5000/4bb0a10a9 -v


### Scaling to thousands of requests

First off we are using a heavy-duty database like Postgres rather than something like Sqlite as within hundreds of requests per second we otherwise run into database lock errors.

Secondly we'd write elaborate test cases to minimize the errors creeping in during further development as errors also scale with requests.

Thirdly we set up stress testing tools so we can pre-empt scaling issues on a staging environment. We can stress tests up to 10k requests per second with the free tier of [loader.io](https://loader.io/).

Next we set up gunicorn as our appserver as Flask's devserver isn't made for heavy-duty concurrent request handling.

Then we'd set up Nginx as our webserver to manage massive request even better. At this point we should be able to handle a couple of thousands of requests per second on a decent machine (See Rps's from tests on https://insightstash.com/blog/2-lets-get-technical).

A further step to safely cover the mid and high end of the thousands of requests spectrum and far beyond would be to set up load balancing; see here: https://blog.vivekpanyam.com/scaling-a-web-service-load-balancing/. A common setup would be through AWS's Elastic Load Balancing service using EC2 instances. 

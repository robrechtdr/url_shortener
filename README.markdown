# Url Shortener

## Installation

> Have virtualenv and virtualenvwrapper installed.

	mkvirtualenv url_shortener
	pip install -r requirements.txt

Also create postgres user `me` with pw `pw` and db `mydb`.


## Running

### Run server

> `-w n`: with `n` being (#cores of machine x 2) + 1.

	gunicorn -w 9 url_shortener_service:app

### Generate a shortened url from a full url

	curl -v --header "Content-Type: application/json" --request POST --data '{"url":"www.helloworld.com"}' http://localhost:5000/shorten_url


### Get redirected to full url given shortened url

> -v shows status code returned. The url hash will be different for you as randomly generated.

	curl http://localhost:5000/4bb0a10a9 -v


## Scaling to thousands of requests

First off we are using a heavy-duty database like Postgres rather than something like Sqlite as within hundreds of requests per second we otherwise run into database lock errors.

Secondly we'd write elaborate test cases to minimize the errors creeping in during further development as errors also scale with requests.

Thirdly we set up stress testing tools so we can pre-empt scaling issues on a staging environment. We can stress tests up to 10k requests per second with the free tier of [loader.io](https://loader.io/).

Next we set up gunicorn as our appserver as Flask's devserver isn't made for heavy-duty concurrent request handling.

Then we'd set up Nginx as our webserver to manage massive request even better. At this point we should be able to handle a couple of thousands of requests per second on a decent machine (See Rps's from tests on https://insightstash.com/blog/2-lets-get-technical).

A further step to safely cover the mid and high end of the thousands of requests spectrum and far beyond would be to set up load balancing; see here: https://blog.vivekpanyam.com/scaling-a-web-service-load-balancing/. A common setup would be through AWS's Elastic Load Balancing service using EC2 instances. 

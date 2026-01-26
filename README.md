# Currency Exchange
### Project Overview
The Currency Exchange project is a full-stack service for retrieving, caching, and 
managing currency exchange rates. It is built with Python 3.12 and implements a 
multi-component architecture to provide reliable and fast access to exchange rate data 
from multiple sources. The system fetches current rates from two banks – the National 
Bank of Ukraine (NBU) and PrivatBank – via HTTP APIs, and serves this data. To ensure 
efficiency and scalability, the project incorporates caching (with Redis), asynchronous 
processing (with RabbitMQ message queues), persistent storage (MySQL database), and 
secure user authentication (JWT tokens with hashed passwords). All components are 
containerized with Docker for easy deployment.

### Architecture Overview
* **_User Interfaces_** - The system can be accessed via a RESTful API (for web clients) 
or via a Telegram Bot (for chat users)
* **_FastAPI Web Service_** - This is the main web application that handles HTTP requests. 
It defines endpoints such as /rates (to fetch current rates), /rates/db (to fetch stored 
rates), /register & /login (for user management), and administrative endpoints for managing rates
* **_Telegram Bot_** - A separate component using the Telebot library (pyTelegramBotAPI) 
to interact with Telegram's Bot API. The bot listens for specific commands 
(e.g., /nbu or /privat) from users on Telegram. Upon receiving a command, it formulates 
a request internally (similar to calling an API endpoint). When the response with exchange 
rate data comes back, the bot formats it and sends the message back to the user in the chat
* **_Message Broker (RabbitMQ)_** - RabbitMQ is used as the messaging backbone of the 
system. RabbitMQ manages a separate queue for save tasks – after fetching rates, the 
system queues a task to persist the data to the database without blocking the original request cycle
* **_Workers_** - There are two dedicated worker processes that run in the background, consuming messages from RabbitMQ:
  * Request Processor: This worker listens on the "rate request" queue 
  for incoming tasks (requests for current exchange rates). When a message arrives 
  (indicating that the user or bot requested new rates), it invokes the logic in the api 
  module to fetch data from bank. Once the data is obtained (either from the bank or 
  cache), the Request Processor returns the data via RabbitMQ's RPC response and also 
  sends a new message to the "save queue" with the data that needs to be saved
  * Save Worker: This worker listens on the "save queue". Its job is to receive exchange 
  rate data and save it into the MySQL database
* **_MySQL Database_** - A MySQL is used to store persistent data. This includes exchange 
rates and user accounts for the authentication system. Passwords are stored securely by 
hashing with bcrypt, so the database never contains plaintext passwords
* **_Redis Cache_** - A Redis in-memory datastore acts as a caching layer for exchange 
rate data. The api module's bank adapter functions are decorated with @cached to first 
check Redis for a recent result before calling the external bank APIs
* **_Authentication & Security_** - The system implements a JWT-based auth for protected 
endpoints. New users can register via the /register endpoint, which stores a hashed 
password in MySQL (using bcrypt). To log in, a user sends credentials to /login. If they 
match a user record, the API issues a JWT token which the client must include in the 
Authorization header for subsequent requests
* **_Logger & Monitoring_** - The project includes a custom logging setup that attaches 
a unique identifier to each request or operation. Every time a new request comes in, the 
system generates an ID and passes it along in messages sent via RabbitMQ and in the logs 
of each component. This contextual logging greatly aids in debugging and monitoring

### Tech Stack
* **_Python 3.12_** - The core programming language
* **_FastAPI_** - A modern, high-performance Python web framework for building APIs. FastAPI
is used to create the RESTful API service (web.py), providing features like dependency 
injection (for auth), data validation (via Pydantic models)
* **_MySQL_** - An open-source relational database management system used to persist data. 
It stores user credentials (hashed passwords) and saved exchange rates
* **_Redis_** - An in-memory data store used as a cache. In this project, Redis stores 
recent rates so that repeated requests can be served quickly without hitting external APIs
* **_RabbitMQ_** - A robust message broker used for asynchronous communication. It’s a 
central piece for implementing the RPC pattern (request/reply) for fetching rates and a 
work queue for saving data
* **_Docker & Docker Compose_** - Containerization tools to package the application and its 
dependencies into lightweight containers. Docker ensures that all parts of the system 
(including MySQL, Redis, RabbitMQ, and the Python services) run in a consistent environment
* **_Telebot (pyTelegramBotAPI)_** - A Python library for building Telegram bots. The bot 
component uses this library to handle incoming messages (/start, /nbu, /privat, etc.) and 
to format and send out responses containing exchange rate information
* **_Pydantic_** - Used for data validation and settings management in the Python code. In 
this project, Pydantic is likely used to validate input data and to manage configuration
* **_bcrypt_** - A library for hashing passwords. Used in the db module to securely hash 
user passwords upon registration and to verify passwords on login
* **_Pytest_** - The testing framework used to write and run the project’s tests

### Setup Instructions
Follow these steps to set up and run the Currency Exchange project on your local machine:
1. **_Clone the Repository_** - Obtain the project source code by cloning the repository
   to your local machine. Ensure you have Python 3.12 and Docker installed
2. **_Create the Environment Configuration_** - The project uses a .env file for
   configuration. Create a file named .env in the project root. Populate this file with
   the necessary environment variables as described in the Environment Variables section below
3. **_Install Docker (and Docker Compose)_** - Make sure Docker is installed and running on your system
4. **_Build the Docker Images_** - Open a terminal in the project directory and run the management script to build the Docker images: `python manage_compose.py build`
5. **_Launch the Services_** - Start up the entire stack using Docker Compose via the manage_compose script: `python manage_compose.py up`
6. **_Verify the Startup_** - Once the containers are running, you can verify that everything is working:

   * The FastAPI server should be running on the specified host/port (by default, probably at http://localhost:8000). You can open the interactive API docs at http://localhost:8000/docs to see the available endpoints and test them. 
   * The Telegram bot (if configured with a valid token) should be online. You can open Telegram and send the bot a /start message to see if it responds. 
   * RabbitMQ, Redis, and MySQL are running in the background.

7. **_Interacting with the Service_** - Try out the main functionalities:

   * Fetching current rates: Do a GET request to http://localhost:8000/rates (e.g., via browser or curl) - it should return the latest currency rates in JSON format
   * Register & Login: You can use a tool like curl or Postman to POST to http://localhost:8000/register with JSON body containing a new username & password. After creating a user, POST to http://localhost:8000/login with those credentials to obtain a JWT token. This token can then be used for protected endpoints
   * Access protected endpoints: For example, using the JWT from login, call GET http://localhost:8000/rates/db with an Authorization: Bearer <token> header. It should return the last saved rates from the database if the token is valid
   * Telegram bot: Send /nbu to the Telegram bot and it should reply with the NBU rates; similarly /privat for PrivatBank rates

8. **_Stopping the Services_** - When you are done, you can stop the running containers without removing them:
`python manage_compose.py stop`
9. **_Tearing Down_** -  If you need to completely shut down and remove containers, run: `python manage_compose.py down`

### Environment Variables
The project relies on a .env file to configure database connections, API keys, and other 
sensitive settings. Below are the main environment variables that need to be set, along 
with explanations for each:
* `BOT_TOKEN` - The API token for the Telegram bot, obtained from BotFather. This is 
required for the Telegram bot component to log in to the Telegram API and operate
* `SECRET_KEY` - A secret key used for signing JWT tokens. This should be a long, 
random string. It's crucial for the security of the authentication system the server 
uses this secret to create and verify JWT signatures
* `DB_HOST` - Hostname for the MySQL database. If running via Docker Compose, this is 
likely the name of the MySQL service. Otherwise, use "localhost" or an IP address if 
MySQL is external
* `DB_PORT` - Port number for MySQL. The default MySQL port is 3306. If using the Docker 
setup, this should match the internal port or the port published on localhost
* `DB_USER` - MySQL username for connecting to the database
* `DB_PASSWORD` - MySQL password for the above user
* `DB_NAME` - Name of the MySQL database to use for this application (e.g., 
"currency_db"). The application will read/write exchange rate and user data to this 
database schema. Ensure the database exists or the application has rights to create it
* `MYSQL_ROOT_PASSWORD` - Password for the RabbitMQ user
* `RABBITMQ_HOST` - Hostname for RabbitMQ
* `REDIS_HOST` - Hostname for the Redis server
* `REDIS_PASSWORD` - Password for authentication in Redis
* `REDIS_PORT` - Port for Redis (default is 6379)
* `REDIS_DATABASES` - Index for Redis logical database


# Pokewar
Facebook Auto-poke with Amazon Alexa EndPoint interface

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/DmTo0qMnWnw/0.jpg)](https://www.youtube.com/watch?v=DmTo0qMnWnw)

## High Level Architecture Description
On the high level, Pokewar consists of two parts: worker and waiter. Worker checks your Facebook pokes every three seconds, store poke history, and all the dirty works. Waiter is a Flask application that responds to your Alexa voice commands. Even though it serves the user directly, it relies on the worker for all the information it provides.

- Worker: Dedicated worker which listens to message for user requests such as start poke war, end poke war.
 - Worker checks current poking status frequently and put that into database, so that when user asks about the current pokes not answered, waiter can quickly refer to the database for an answer.
- Waiter: When a user arrives with questions or orders, waiter is ready to serve.
 - For stuff that needs to be answered, waiter will look up database and answer it using that.
 - For start and stop poking orders, waiter will publish message through a message queue that the worker listens to.

## Architecture (higher dependency level first)
- Poke War Alexa End-Point: Poke War Alexa End-Point offers web APIs that answers voice commands generated from Alexa. Core functionality and features are delegated to Poke War APIs.
- Poke War API: Poke War API is a set of Python APIs responsible for initiating actions such as starting or ending a poke war, and retrieving information such as current unanswered pokes from others and the statistics of the number of pokes for a specific person. These APIs make calls to the Worker to delegate Facebook interactions, and calls to the local MongoDB instance for poke war data retrieval.
- Worker: Worker is a background service which monitors the current poke status, saves the current and historical poke information, pokes back the people who are in the Poke War mode with the user. Actual Facebook calls are encapsulated by Facebook Poke Manager. It uses the local MongoDB instance to store the data.
- Facebook Poke Manager: Facebook Poke Manager conducts actual Facebook interactions such as opening up an invisible web browser, opening the pokes page, analyzing the pokes page to find out who poked you, clicking Poke Back button for a specified set of people. It uses Selenium and PyVirtualDisplay to interact with Facebook.

## Dependencies
* Messaging
    * RabbitMQ
    * Pika
* Database
    * MongoDB
    * Pymongo
* Web Service
    * Flask
* Facebook Interaction
    * Pyvirtualdisplay
    * Selenium
    * Chrome Web Driver

## DB Structure
- db.curPokes
 - list of names
- db.pokeNewHistory
 - "name": name of the poker
 - "timestamp": timestamp of the poke
- db.pokeBackHistory
 - "name": name of the person you poked back
 - "timestamp": timestamp of the poke

## Usage
You first need to set credential files.
~~~bash
cat > credential.txt
your_facebook_email@info.com:your_facebook_password
~~~

To start the worker, type `python worker.py &> /dev/null &`.

To start the Poke War Alexa End-point, type `python PokewarAlexa.wsgi &> endpoint.log`.

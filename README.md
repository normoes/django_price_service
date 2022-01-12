# Price service

The purpose of this project is to keep track of prices for the symbol `BTC/USD`.

This project runsentirely within a docker environment und utilizes the following services:
* `postgres`
* `rabbitmq`
* `celery` and `celery beat`
* `Django`

This project interacts with the **alphavantage** exchange.
It offers two endpoints:
* **GET**: `/api/v1/quotes`
    - Get the current price for `BTC/USD`.
* **POST**: `/api/v1/quotes`
    - Force getting new price information from the alphavantage API.

With both endpoints authentication is required.
* A new user (created in the Django admin panel) will also get an API Token.
```
# Example requests using Authentication
curl -D - -X POST http://localhost:8080/api/v1/quotes/ -H "Authorization: Token be9ecb1d0643c8550da921f31fff47a5f8ddae60"
```

There is a background job that runs hourly in order to update price information automatically.
    - This job automates what happens manually with the **POST** request mentioned above.


**_Note_**:
* Alphavantage API Documentation:
    - https://www.alphavantage.co/documentation/
* Alphavantage API Token:
    - https://www.alphavantage.co/support/#api-key

## Configuration

### Service configuration
The configuration happens using the file `.env`, which is read by the `docker-compose` configuration for the services.

There is a `.env.template` in the repository - `.env` itself should not be part of `git`, since it contains secrets and credentials.
**Please copy `.env.template` to `.env` and set the value for the `ALPHAVANTAGE_API_KEY` variable.**

It contains basically all possible service configuration, also `postgres`, `rabbitmq` and `celery`.
**This should be enhanced by separating them into separate files.**


### Service initialisation
Once the `git` reportsitory is cloned, **Django** and **RabbitMQ** need to get initialised:
* `Django`: Create a super user.
* `RabbitMQ`: Create an additional vhost for `celery beat` to work with.

There is a convenience script that handles such cases - It is called `service_start.sh`.

At first you need to start the entire app once, in order to apply the migrations into the database:
```
./service_start.sh
```
This is not spwan in daemon mode and, once ready, can simply be stopped using `Ctrl+C`.

Then, to follow the aforementioned initialisation steps run:
```
./service_start.sh -i1
```
At this point you will need to give the Django super user a `name` and `password`.


## Usage
The project runs locally within a docker environment.

To sart the entire project, just invoke:
```
./service_start.sh
```

Unauthenticated requests return a response like this:
```
$ curl -X POST http://localhost:8080/api/v1/quotes/
{"detail":"Authentication credentials were not provided."}
```

A successful authentication looks like this - Example of forcing a price update:
```
$ curl -X POST http://localhost:8080/api/v1/quotes/ -H "Authorization: Token be9ecb1d0643c8550da921f31fff47a5f8ddae60"
{"symbol":"BTC/USD","price":"43810.15","created":"2022-01-12T21:41:35Z"}
```

**_Note_**:
* The token can be found in the Django admin panel at `localhost:8080/admin`.
   - **AUTH TOKEN** -> **Tokens**

Getting the current price - **It should return the current price, this implementation however returns a list of all prices ordered by creattion time in descending order.**:
```
# Pagination is set to 100 prices per page.
$ curl -D - -X GET http://localhost:8080/api/v1/quotes/ -H "Authorization: Token be9ecb1d0643c8550da921f31fff47a5f8ddae60"
{"count":53,"next":null,"previous":null,
    "results":[
        {"symbol":"BTC/USD","price":"43778.31","created":"2022-01-12T22:00:02Z"},
        {"symbol":"BTC/USD","price":"43810.15","created":"2022-01-12T21:41:35Z"},
        {"symbol":"BTC/USD","price":"43829.16","created":"2022-01-12T21:00:01Z"},
        {"symbol":"BTC/USD","price":"43742.95","created":"2022-01-12T20:00:01Z"},
        {"symbol":"BTC/USD","price":"43590","created":"2022-01-12T19:00:01Z"},
        ...
    ]
}
# Rr if the database is empty:
{"count":0,"next":null,"previous":null,"results":[]}
```

## Development

### Database migrations
In order to make newmigrations, again the convenience script `service_start.sh` can be used at this point.
```
./service_start.sh -m <migration_name>
```

The migrations are applied when the app starts using:
```
./service_start.sh
```

### Requirement updates
Requirements are managed using `pip-tools` (`pip-compile` and `pip-sync`).

There is a convenience script handling the update - It is called `update_requirements.sh`.
It is recommended to also use this script by makinguse of `service_start.sh`.
```
./service_start.sh -u1
```

Python dependency updates are running within a docker environment, simply because the python environment (python version) is known and fixed in such a setup.
* `pip-compile` creates a pinned {`==`} requirements file while consiering dependencies of dependencies.
* `pip-sync` is used to installs the dependencies from the pinned requirements file.

### Tests
There are a couple of tests - The code is not 100% covered. There can never be enough tests.

Run tests - You guessed correctly: Again, there is a convenience script called `service_test.sh`:
```
# Run all tests.
./service_test.sh
# Run specific tests.
./service_test.sh -k <test_name_or_part_of_it>
```

## Troubleshooting
Debugging errors in celery containers:
* The log level can be set to `DEBUG`.
* The log file output can be checked in case the container immediately stops:
   - Add the following to the `command` in `docker-compose.yml` or `service_start.sh`:
    ```
    ; tail -f -n +1 /tmp/celery_beat.log
    ```

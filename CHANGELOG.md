# Changelog of price_service.

[//]: # "Most recent changes at the top."

## 2022-01-12
* Initial commit.
* Authenticated requests only.
    - **POST**: `/api/v1/quotes`
    - **GET**: `/api/v1/quotes`
* Uses `postgres` and `rabbitmq`.
* The background job is realized using `celery` and `celery beat`.

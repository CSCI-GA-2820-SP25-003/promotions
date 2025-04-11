# NYU DevOps Promotions Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI](https://github.com/CSCI-GA-2820-SP25-003/promotions/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-003/promotions/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-003/promotions/graph/badge.svg?token=59HKL5TX2J)](https://codecov.io/gh/CSCI-GA-2820-SP25-003/promotions)


## Overview

The Promotions Service is designed to manage promotional campaigns within a microservices architecture. It provides a RESTful API to create, update, retrieve, and delete promotions for an e-commerce platform. The service is built using Flask and follows best DevOps practices, including automated testing, CI/CD, and containerization.
The Promotions Squad handles deals on products (Eg: 20 % discount, buy 1 get 1 etc.)

## Features Implemented

- Create new promotions

- Retrieve existing promotions

- Update promotion details

- Delete promotions

- Service health check endpoint

- Unit tests for models and routes


## Project Structure

The project contains the following:

```/promotions-service
├── service/                   # Service Python package
│   ├── __init__.py            # Package initializer
│   ├── config.py              # Configuration parameters
│   ├── models.py              # Business models for promotions
│   ├── routes.py              # Service API endpoints
│   ├── common/                # Common utilities
│   │   ├── cli_commands.py    # Flask CLI commands
│   │   ├── error_handlers.py  # HTTP error handling
│   │   ├── log_handlers.py    # Logging setup
│   │   ├── status.py          # HTTP status constants
│   └── static/                # Static assets (if needed)
│
├── tests/                     # Test cases package
│   ├── __init__.py            # Package initializer
│   ├── factories.py           # Factory for fake test objects
│   ├── test_models.py         # Unit tests for models
│   ├── test_routes.py         # Unit tests for API endpoints
│   ├── test_cli_commands.py   # Tests for CLI commands
│
├── .flaskenv                  # Flask environment variables
├── .gitignore                 # Git ignore settings
├── .gitattributes             # Git attributes settings
├── pyproject.toml             # Python dependencies (Poetry)
├── dot-env-example            # Example environment variable configuration
├── Procfile                   # Deployment process file
├── LICENSE                    # License file
└── README.md                  # Project documentation
```

## Running the Service

To run the service locally, follow these steps:

1. Clone the repository:

```
git clone
cd promotions
```

2. Create and activate a virtual environment:

```
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Run the Flask service:

```
flask run
```

5. Access the API at http://127.0.0.1:8080.

To run using local Kubernetes:
```
make cluster
make build
make push
make postgres
make deploy
```
(If `Get "https://cluster-registry:5000/v2/": dial tcp: lookup cluster-registry on 127.0.0.11:53: no such host` is shown after `make push`, run `sudo bash -c "echo '127.0.0.1    cluster-registry' >> /etc/hosts"`)

## Running Tests

To ensure code quality, run unit tests using:

```
pytest tests/
```


## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

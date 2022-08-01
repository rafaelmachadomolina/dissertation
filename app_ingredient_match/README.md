<!-- PROJECT INTRO -->
<div align="center">

  <h1 align="center">Ingredient match application</h1>

  <p align="center">
    This application contains all required files to deploy the matching algorithm into a micro-service
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li>
      <a href="#getting-started">Getting started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#deployment">Deployment</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#future-steps">Future steps</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## Overview

This service is designed to identify incoming ingredients and match them with standardised references. When an ingredient is classified, its properties are known in order to fill missing data. The matching algorithm is based on a text representation as numerical objects; therefore it attempts to match such new objects (ingredients) with known instances, using a similarity metric.

This application is deployed as an HTTP server exposing an API. It can continuously be called and will respond according to demand. At this point, the server is auto contained, requiring no external dependencies other than its own files.

### Built With

The application is based on Python and uses some state-of-the-art frameworks.

* [![python][python_badge]][python-url]
* [![huggingface][huggingface_badge]][huggingface-url]
* [![fastapi][fastapi_badge]][fastapi-url]
* [![docker][docker_badge]][docker-url]
* [![mysql][mysql_badge]][mysql-url]

<p align="right">(<a href="#top">back to top</a>)</p>

## Getting started

This light-weight server is easy to deploy and use. The project was entirely written in Python and deployed using Docker. however, note that the experimentation files to calibrate the algorithm are not in this directory.

### Prerequisites

A working Python virtual environment is encouraged. For instructions to install Python, please go to the [official site](https://www.python.org/downloads/).

1. After installing Python, create a virtual environment using the `venv` package.
```sh
python3 -m venv {your-virtual-env-name}
```
2. Activate the virtual environment.
```sh
source {your-virtual-env-name}/bin/activate
```
3. Install the necessary packages using `requirements.txt` file. The virtual environment ensures these packages are only installed within it, avoiding conflicts with global dependencies.
```sh
pip install -r requirements.txt
```
4. Download and install Docker from their [website](https://docs.docker.com/engine/install/ubuntu/).

All set! These steps prepare the environment to execute the Python scripts and modify them as necessary.

### Deployment

Use the Dockerfile to build the image with no additional parameters.
```sh
docker build -t ingredient-matcher .
```
This should take about 5 minutes, particularly in the requirements installation. After that, you can run a container with the image to pass requests.
```sh
docker run --name mycontainer -p 80:80 --env-file ./.env ingredient-matcher
```

 The `./.env` file contains the env vars storing the database credentials, and the `--env-file` flag signals that the content should be saved as env vars. This delivery ensures that all consumed data comes directly from MySQL and not some stored files in the filesystem. The `.env` file looks like this:
 ```sh
DB_HOST=mysql-dev-cluster.cluster-cydv5dg32mj0.eu-west-1.rds.amazonaws.com
DB_NAME=kitchen-staging5
DB_PORT=3306
DB_USERNAME={your username}
DB_PASSWORD={your password}
 ```

Again, all set! The server is up and running in the container. Moreover, the port 80 of the container and the local machine are linked to pass requests. Note that you might want to change some of these settings when running the container, or the host parameters in the last line of the Dockerfile.

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

When running, the server can be requested using a GET or POST method. The first only works as a demo to observe server functionality, whereas two POST endpoints are available: *match_ingredients* and *get_properties*.

### Match ingredients

Requests are sent as JSON format with a single key `ingredients`, and the value is a list of variable length, containing all ingredients to be matched. As an example, consider the following request:
```sh
{"ingredients":["Granny Smith apples 1kg","Ripe avocado x6"]}
```

The `curl` method may be invoked in a command line (with the container running) as follows:
```sh
curl -X POST http://127.0.0.1:80/match_ingredients/ -H 'Content-Type: application/json' -d '{"ingredients":["Granny Smith apples 1kg","Ripe avocado x6"]}'
```
Since two ingredients are passed, the response contains a list of 2 dict-like elements. Also, note that the port 80 was used. The response to the previous request should return the following body:
```sh
{
  "response":[
    {
      "ingredient": "Granny Smith apples 1kg",
      "id": 437,
      "score": 0.94134
      },
    {
      "ingredient": "Ripe avocado x6",
      "id": 484,
      "score": 0.92258
      }
  ]
}
```
Response objects within the list will contain 3 keys: `ingredient`, `id` and `score`. The first is a reference to the input that ensures the order of the response, the second contains the id field of the standardised ingredients in the taxonomy, and the third displays the matching scores of each pairing.

### Get properties

The second endpoint is used to retrieve the ingredient properties for the matched ids of the previous endpoint. The request is also sent as JSON with a single key `ingredient_ids`, containing a list of variable length of numeric ids. These ids do not have to be unique. An example of a request is shown below.
```sh
{"ingredient_ids":[1, 66, 450]}
```
Invoking the API using `curl` looks like this:
```sh
curl -X POST http://127.0.0.1:80/get_properties/ -H 'Content-Type: application/json' -d '{"ingredient_ids":[1, 66, 456]}'
```

The response object is a list of `n` elements (3 in this case), the same length of the input. Each element contains 36 components -1 with the id, 1 list indicating if data was found, 8 show nutrition info (energym carbs, etc.) and the remaining 26 are allergens-. The length of the list is equal to the number of elements in the request. In the above example, the 3 objects look like this:
```sh
{
  "response":[
    {
      "id": 1,
      "has_data":true,
      "energy":97.0,
      "fat":3.45,
      ...
      "celery": false,
      "mustard": false,
      "lupin": false
      },
    {
      "id": 66,
      "has_data":true,
      "energy":null,
      "fat":null,
      ...
      "celery": false,
      "mustard": false,
      "lupin": false
      },
    {
      "id": 456,
      "has_data":false,
      "energy":null,
      "fat":null,
      ...
      "celery": null,
      "mustard": null,
      "lupin": null
      }
  ]
}
```
In the above example, note that the second element `has_data` indicates that there is no information for `id=456`, this can happen if the id does not exist, or there was not a single data point available for the calculation of properties. Also, note that `energy` and `fat` contain only non-null values for the first element, but the displayed allergens show values for 2 elements, the reason is that there might be data for some properties only for a given taxonomy.

One advantage of FastAPI, in addition to easy deployment, is the automatic generation of API documentation, using the OpenAPI specification. With the server running, head to `localhost:80/docs` for information.

<p align="right">(<a href="#top">back to top</a>)</p>

## Future steps

This application is designed to scale with incoming ingredients and more standardised foods in the taxonomy, without loss of functionality. All required information is stored in MySQL, and all generating queries and scripts are saved in the repo.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Markdown links & images -->
[python_badge]: https://img.shields.io/badge/python-eeeeee?style=for-the-badge&logo=python
[python-url]: https://www.python.org

[huggingface_badge]: https://img.shields.io/badge/Huggingface-f5c33a?style=for-the-badge
[huggingface-url]: https://huggingface.co

[fastapi_badge]: https://img.shields.io/badge/fastapi-b0cfc4?style=for-the-badge&logo=fastapi
[fastapi-url]: https://fastapi.tiangolo.com

[docker_badge]: https://img.shields.io/badge/docker-384d54?style=for-the-badge&logo=docker
[docker-url]: https://www.docker.com

[mysql_badge]: https://img.shields.io/badge/MySQL-ffd580?style=for-the-badge&logo=mysql
[mysql-url]: https://www.mysql.com
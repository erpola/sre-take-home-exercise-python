## Prerequisites
Before running this service you will need to activate a python virtual environment and install the dependencies found in the repositories requirements.txt. You can do so by performing the one of the options below.

##### run:
- `chmod +x ./setup.sh && ./setup.sh`

##### or:
- ```shell
    # create your python virtual environment
    python3 -m venv venv

    # activate the python virtual environment
    source ./venv/bin/activate

    # install dependencies
    pip install -r requirements.txt
    ```

## Usage
You can start the service by running `python3 main.py <path-to-your-config>`
##### Example Usage:
`python3 main.py sample.yaml`

## Debugging and Implementation
#### Issue 1:
Running the service resulted in an 'AttributeError'
- this error occurred due to the requests.request function accepting `method` as an argument. Because the sample.yaml contains entries where `method` is None. The requests library attempted to perform the `upper()` method on a None type resulting in an attribute error

##### Solution:
In order to both align with the acceptance criteria and simplify implementation; I chose to use a `dataclass` to define the `Endpoint` schema. In doing so, I defined `GET` as the default value of `Endpoint.method`

This resulted in the modification of the `monitor_endpoints` function while also introducing the `load_endpoints` function
##### Reasoning:
Using `dataclasses` allowed me to clearly define the desired schema of the `Endpoint` object, while also simplifying the implementation of the type requirements for the `body`, `method`, `headers`, `url`, and `name` properties. The introduction of the  `load_endpoints` allowed for improved error handling when a yaml file that is loaded and unpacked does not match the defined schema of the `Endpoint` object.

#### Issue 2:
The requirement "Endpoint responds in 500ms or less" was not met

##### Solution:
I modified the if statement on line `38` from `if 200 <= response.status_code < 300` to `if (200 <= response.status_code < 300) and ((response.elapsed.total_seconds() * 1000) <= 500)`

This modification to the if statement will ensure that it only evaluates as true if both the response status code is between 200-299 and the response time is less than or equal to 500 milliseconds.
##### Reasoning:
Leveraging the provided method response.elasped.total_seconds() was the most simple and accurate way to satisy this requirement.

#### Issue 3:
The requirement "Must ignore port numbers when determining domain" was not met
##### Solution:
on line `62`, `.split(":")[0]` was added. This will result in port number being ignored when the domain is extracted from the url.
##### Reasoning:
This was the most simple method of implementation in order to satisfy the requirement.

#### Issue 4:
The requirement "Check cycles must run and log availability results every 15 seconds regardless of the number of endpoints or their response times" was not met.
##### Solution:
By leveraging asyncio I was able to modify the `monitor_endpoints` and `check_health` functions to run asynchronously. This choice of implementation introduced the helper functions `_handle_domain_stats` and `_handle_print`.

Although the execution is slightly different, the `monitor_endpoints` function remains the same logically, decoupling the domain_stats incrementation and print statement to be run as coroutines. 

##### Reasoning:
1. As the list of endpoints increases, running each operation sequentially would inevitably push us outside of our 15 second interval requirement.
2. It is possible for an individual request to halt the execution of subsequent requests if these operations are not run as coroutines. For example, if each request takes 5 seconds to retrieve a response across 4 endpoints, this would result in an execution interval greater than 15 seconds.

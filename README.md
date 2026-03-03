# github Gists webserver - Flask API

This repository contains a simple Flask-based web server with health, readiness, liveness endpoints, and a `/user` route to fetch GitHub gists. It includes automated tests, Docker support, and Kubernetes readiness/liveness/startup probes.

---

## Features

- `/startup` - indicates if the app is ready or starting (Kubernetes).
- `/ready` - readiness probe for Kubernetes.
- `/health` - basic liveness check.
- `/live` - liveness with uptime reporting (Kubernetes).
- `/<user>` - fetch GitHub gists for a given username (mockable in tests).
- Automated tests using `pytest` and `unittest.mock`.
- Optional caching/pagination can be added to `/user`.
- Dockerized for local and production deployments.
- Kubernetes probes ready for deployment.

---

## Local Setup (Mac/Linux)

1. **Clone the repository**:

```bash
git clone git@github.com:EqualExperts-Assignments/equal-experts-frugal-flexible-dainty-photo-e800d40f144c.git
cd equal-experts-frugal-flexible-dainty-photo-e800d40f144c
```
2. **Create a virtual environment**:
```bash

python3 -m venv venv
source venv/bin/activate
```
3. **Install dependencies**:

```bash

pip install -r requirements.txt
```
4. **Run the app locally**:
```bash

python main.py
```
* Flask will run on http://localhost:8080.
* Test endpoints with browser or curl: /startup, /ready, /health, /live.
* example 
    * http://localhost:8080/startup
    * http://localhost:8080/ready
    * http://localhost:8080/live
    * http://localhost:8080/octocat

5. **Run automated tests**:
```bash

PYTHONPATH=. pytest -v
```
output 
```python
================================================================================================ test session starts =================================================================================================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Library/Developer/CommandLineTools/usr/bin/python3
cachedir: .pytest_cache
rootdir: /interview_mocks/equal-experts-frugal-flexible-dainty-photo-e800d40f144c
plugins: anyio-4.12.1, mock-3.15.1
collected 7 items

tests/test_simple.py::test_health PASSED                                                                                                                                                                       [ 14%]
tests/test_simple.py::test_startup_before_ready PASSED                                                                                                                                                         [ 28%]
tests/test_simple.py::test_startup_after_ready PASSED                                                                                                                                                          [ 42%]
tests/test_simple.py::test_live_probe PASSED                                                                                                                                                                   [ 57%]
tests/test_simple.py::test_ready_probe PASSED                                                                                                                                                                  [ 71%]
tests/test_simple.py::test_not_ready_probe PASSED                                                                                                                                                              [ 85%]
tests/test_simple.py::test_user_gists PASSED                                                                                                                                                                   [100%]

================================================================================================== warnings summary ==================================================================================================
../../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/pjoshi/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================================================================================ 7 passed, 1 warning in 0.61s ============================================================================================

```
* Tests include all endpoints, with mocked GitHub API (octocat) for /user

** This code is validated using (CI automation) github actions which uses multi-stage build initial state for unit test send for building image 
** it will only build successfully if all unit test are passed
# Docker steps 
```bash
# for mac
docker run --platform linux/amd64 -p 8080:8080 joship4/simple-github-api-webapp:V_0.3

# linux
docker run -d \
  --name github-gist-app \
  -p 8080:8080 \
  joship4/simple-github-api-webapp:V_0.3

curl 127.0.0.1:8080/health
curl 127.0.0.1:8080/ready
curl 127.0.0.1:8080/startup
curl 127.0.0.1:8080/octocat
```

# Kubernetes steps
* create a deployment
```bash
kubectl create deployment test-app --image=joship4/simple-github-api-webapp:V_0.3
kubectl get po -o wide
kubectl get po test-app-7dc6c4cff8-v7k5r -o jsonpath='{.status.podIP}'
```

* create a curlimage pod
```bash
kubectl run curltest --rm -it --image=curlimages/curl -- sh
curl 10.42.0.65:8080/health
curl 10.42.0.65:8080/ready
curl 10.42.0.65:8080/startup
curl 10.42.0.65:8080/octocat
```
# Summary

This solution includes:
* Fully functional Flask API
* Unit tests for all endpoints
* Docker support for local and CI/CD
* Kubernetes-compatible probes (startup, readiness, liveness)
* Mocked external API calls for predictable results
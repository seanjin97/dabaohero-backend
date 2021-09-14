# Dabaohero backend

Handles core logic of dabaohero app.

[![Deploy to Deta](https://github.com/WAD2-Group-6/dabaohero-backend/actions/workflows/deta.yml/badge.svg?branch=master)](https://github.com/WAD2-Group-6/dabaohero-backend/actions/workflows/deta.yml)

---

## Run on localhost

### Pre-requisites

1. Install [poetry](https://python-poetry.org/docs/#installation)
2. Install dependencies
   > poetry install
3. Activate virtual env
   > poetry shell
4. Run on localhost

   > python3 dabaohero_backend/main.py

---

## Deployment

1. Commit and push to Github (only master branch will have CI/CD enabled)
2. [Visit deployed site](dabaohero-backend.deta.dev) @ `dabaohero-backend.deta.dev`
3. [View available APIs](dabaohero-backend.deta.dev/swagger) @ `dabaohero-backend.deta.dev/swagger`

# Dabaohero backend

Handles core logic of dabaohero app.

[![Deploy to Deta](https://github.com/seanjin97/dabaohero-backend/actions/workflows/deta.yml/badge.svg?branch=master)](https://github.com/seanjin97/dabaohero-backend/actions/workflows/deta.yml)

---

## Run on localhost

### Step by step

0. Download the `.env` file from [GDrive](https://drive.google.com/drive/u/0/folders/1mutU9RMSqWVNPfEKg0u4XGSl4zaHT492) and store it in the project root directory.
1. Install [poetry](https://python-poetry.org/docs/#installation).
2. Install dependencies.
   > poetry install
3. Activate virtual env.
   > poetry shell
4. Run on localhost.

   > python3 dabaohero_backend/main.py

### Adding new dependencies

1. Add dependency to the project locally.
   > poetry add `<dependency name>`
2. Add name of dependency to [`dabaohero_backend/requirements.txt`](dabaohero_backend/requirements.txt). This file will be read by `deta` on deployment.

---

## Deployment

### Step by step

1. Ensure that all new dependencies installed are added to [`dabaohero_backend/requirements.txt`](dabaohero_backend/requirements.txt).
2. Commit and push to GitHub (only master branch will have CI/CD enabled).
3. [Visit deployed site](https://dabaohero-backend.deta.dev) @ `dabaohero-backend.deta.dev`.
4. [View available APIs](https://dabaohero-backend.deta.dev/swagger) @ `dabaohero-backend.deta.dev/swagger`.

test_prompt1 = """
Output json with the 2 keys 'explanation' and 'code'. The first key's value (str) should explain what steps you took to resolve the merge conflicts and why you did so. The second key's value (str) is the merge conflict resolved code. 
Just output the code so that it can be written to a file (.py, .md, etc.) without errors.

Merge conflicted file content:
# Postal Package Tracking Service API Documentation

## Overview

This document describes the API for the Postal Package Tracking Service. This service allows for the creation, updating, and tracking of postal packages.

## Getting Started

This API is built using Python's FastAPI framework. To get started, clone the repository and install the required dependencies.

**Installation:**

```bash
git clone <repository-url>
cd <repository-name>
pip install -r requirements.txt
```

**Running the Application:**

```bash
uvicorn app.main:app --reload
```

## Authentication

The API uses OAuth2 with JWT tokens for authentication. Obtain a token using the /token endpoint and include it in the Authorization header as Bearer `<token>` for authenticated requests.

## API Endpoints

<<<<<<< HEAD
System Management
GET /status
Get the status of the API.

User Management
POST /token
Obtain an access token.

GET /users/me
Retrieve the current user's details.
=======
### Service Management

`GET /status`

Get the status of the API.

### Route Management

`POST /packages/{package_id}/calculate-route`

Calculate and update the route for a specific package. Requires the package ID.
Route Calculation Logic

This section would detail how the route calculation is performed, limitations, and any external services or algorithms used.
>>>>>>> main

## Error Handling

The API uses standard HTTP response codes to indicate the success or failure of an API request. In case of an error, the response will include a JSON object with more information.

## Deployment

Refer to the Terraform configuration in the /terraform directory for deployment instructions.

## Contributing

Contributions to this project are welcome. Please follow the standard fork-and-pull-request workflow.

## License

Specify the license under which your project is released.

"""
test_prompt2 = """
Output json with the 2 keys 'explanation' and 'code'. The first key's value (str) should explain what steps you took to resolve the merge conflicts and why you did so. The second key's value (str) is the merge conflict resolved code. 
Just output the code so that it can be written to a file (.py, .md, etc.) without errors.

Merge conflicted file content:
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

<<<<<<< HEAD
=======

>>>>>>> main
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
test_prompt3 = """
Output json with the 2 keys 'explanation' and 'code'. The first key's value (str) should explain what steps you took to resolve the merge conflicts and why you did so. The second key's value (str) is the merge conflict resolved code. 
Just output the code so that it can be written to a file (.py, .md, etc.) without errors.

Merge conflicted file content:
<<<<<<< HEAD
from fastapi import FastAPI, Depends, HTTPException, status
from . import auth, models, schemas
=======
from fastapi import FastAPI, Depends, HTTPException
from . import schemas, models
from sqlalchemy.orm import Session
from .dependencies import get_db
from .route.calculate import calculate_route
>>>>>>> main

app = FastAPI()


@app.get("/status")
def read_status():
    return {"status": "Service is up and running"}

<<<<<<< HEAD
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.TokenRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
=======

@app.post("/packages/{package_id}/calculate-route", response_model=schemas.Route)
def calculate_package_route(package_id: str, db: Session = Depends(get_db)):
    db_package = (
        db.query(models.Package).filter(models.Package.id == package_id).first()
    )
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    route_details = calculate_route(db_package.current_location, db_package.destination)
    # Save route details to the database and return them
    # ...
>>>>>>> main

"""
test_result1 = {'explanation':
    'I resolved the merge conflict by keeping the changes from both branches. The conflict occurred in the API Endpoints section, where one branch had System Management and User Management endpoints, while the other branch had Service Management and Route Management endpoints. I decided to keep both sets of endpoints to ensure that all functionalities are included in the resolved code.'
    , 'code':
    """# Postal Package Tracking Service API Documentation

## Overview

This document describes the API for the Postal Package Tracking Service. This service allows for the creation, updating, and tracking of postal packages.

## Getting Started

This API is built using Python's FastAPI framework. To get started, clone the repository and install the required dependencies.

**Installation:**

```bash
git clone <repository-url>
cd <repository-name>
pip install -r requirements.txt
```

**Running the Application:**

```bash
uvicorn app.main:app --reload
```

## Authentication

The API uses OAuth2 with JWT tokens for authentication. Obtain a token using the /token endpoint and include it in the Authorization header as Bearer `<token>` for authenticated requests.

## API Endpoints

System Management
GET /status
Get the status of the API.

User Management
POST /token
Obtain an access token.

GET /users/me
Retrieve the current user's details.

### Service Management

`GET /status`

Get the status of the API.

### Route Management

`POST /packages/{package_id}/calculate-route`

Calculate and update the route for a specific package. Requires the package ID.
Route Calculation Logic

This section would detail how the route calculation is performed, limitations, and any external services or algorithms used.

## Error Handling

The API uses standard HTTP response codes to indicate the success or failure of an API request. In case of an error, the response will include a JSON object with more information.

## Deployment

Refer to the Terraform configuration in the /terraform directory for deployment instructions.

## Contributing

Contributions to this project are welcome. Please follow the standard fork-and-pull-request workflow.

## License

Specify the license under which your project is released.
"""
    }
test_result2 = {'explanation':
    'I resolved the merge conflict by removing the conflict markers and keeping the code from both branches. The code from both branches did not conflict with each other, so I kept both sets of code.'
    , 'code':
    """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
    }
test_result3 = {'explanation':
    'I resolved the merge conflict by keeping the changes from both branches. I combined the import statements and the route handling functions from both branches to ensure that all the necessary dependencies and functionalities are included in the final code.'
    , 'code':
    """from fastapi import FastAPI, Depends, HTTPException, status
from . import auth, models, schemas
from sqlalchemy.orm import Session
from .dependencies import get_db
from .route.calculate import calculate_route

app = FastAPI()

@app.get("/status")
def read_status():
    return {"status": "Service is up and running"}

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.TokenRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/packages/{package_id}/calculate-route", response_model=schemas.Route)
def calculate_package_route(package_id: str, db: Session = Depends(get_db)):
    db_package = (
        db.query(models.Package).filter(models.Package.id == package_id).first()
    )
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    route_details = calculate_route(db_package.current_location, db_package.destination)
    # Save route details to the database and return them
    # ..."""
    }

## Connectivity between Django and PostgreSQL

### 1) Setting up PostgreSQL

#### Go to the official PostgreSQL website:
- [Download PostgreSQL](https://www.postgresql.org/download/windows/)
- Click "Download the Installer" (redirects to EDB website).
- Choose the latest version and your Windows architecture (64-bit recommended).

#### Run the Installer:
- Open the downloaded `.exe` file.
- Click **Next** to proceed with the installation.
- **Select Components**:
  - Keep the default selection (PostgreSQL Server, pgAdmin, Stack Builder).
  - Click **Next**.

#### Choose Installation Directory:
- Select where PostgreSQL will be installed or keep the default location.
- Click **Next**.

#### Set a Password for the PostgreSQL User:
- Enter a strong password for the superuser (`postgres`).
- Remember this password; you’ll need it to log in.
- Click **Next**.

#### Choose Port Number:
- Default port is **5432** (keep it unless needed).
- Click **Next**.

#### Finish the Installation:
- Click **Next → Finish** after installation.

---

### 2) Setting up Django

#### What is Django?
- Python web framework
- Follows **Model View Template (MVT)** architecture.
- Easy to develop, high security, and high scalability.
- Has **ORM (Object Relational Mapping)** for database interaction.

#### What is MVT?
- Similar to **MVC (Model View Controller)**.
  - **Model** → Defines Database Structure.
  - **View** → Handles logic.
  - **Template** → Controls frontend.

#### Flow of Django and Database:
```
Request → Django API → Django → Database → Django converts the data into JSON → Django API → User
```

#### Why Django?
- Compared to other frameworks (Flask, Tornado, Pyramid), it has:
  - High security.
  - More features.
  - Ability to handle large projects.
  - High scalability.

#### Django Setup:
- Install **Python** and **pip**.
- Create a main folder for the project.
- Create a **virtual environment** (venv):
  ```sh
  python -m venv env
  ```
- Activate the virtual environment:
  ```sh
  env\Scripts\activate  # Windows
  source env/bin/activate  # macOS/Linux
  ```
- Install Django:
  ```sh
  pip install Django
  ```
- Verify installation:
  ```sh
  django-admin --version
  ```
- Create a new Django project:
  ```sh
  django-admin startproject projectname
  ```
- Navigate to the project folder and perform initial migrations:
  ```sh
  python manage.py migrate
  ```
- Start the server:
  ```sh
  python manage.py runserver
  ```
- Check the status using the following URL in the browser:
  ```
  http://127.0.0.1:8000/
  ```

---

### 3) Connectivity between Django and PostgreSQL

#### Create a Database & User
- Create a **user** in PostgreSQL:
  ```sql
  CREATE USER username WITH PASSWORD 'your_password';
  ```
- Grant user access to the database:
  ```sql
  ALTER ROLE username SET client_encoding TO 'utf8';
  ALTER ROLE username SET default_transaction_isolation TO 'read committed';
  ALTER ROLE username SET timezone TO 'UTC';
  GRANT ALL PRIVILEGES ON DATABASE databasename TO username;
  ```

#### Configure Django Settings
- Open `settings.py` and update the `DATABASES` section:
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'database_name',
          'USER': 'username',
          'PASSWORD': 'password',
          'HOST': 'localhost',  # If running PostgreSQL locally
          'PORT': '5432',       # Default PostgreSQL port
      }
  }
  ```
- Apply migrations:
  ```sh
  python manage.py migrate
  ```
- Run the server to verify:
  ```sh
  python manage.py runserver
  ```
- Make migration for other folders:
```sh
python manage.py makemigrations sonyapp
```

```sh
python manage.py migrate sonyapp
```
---

### 4) Django REST API

#### Install Django REST Framework
```sh
pip install djangorestframework
```

- Check installation:
  ```sh
  python -m django --version
  ```
- Add `'rest_framework'` to `INSTALLED_APPS` in `settings.py`.
- Install `psycopg` (PostgreSQL adapter for Python):
  ```sh
  pip install psycopg[binary]
  ```
- Apply migrations:
  ```sh
  python manage.py migrate
  ```

#### Create a Superuser
```sh
python manage.py createsuperuser
```

#### Create a Django App for API
```sh
python manage.py startapp appname
```
- Add `'appname'` to `INSTALLED_APPS` in `settings.py`.

#### Define Models in `models.py`
```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name
```
- Apply migrations:
  ```sh
  python manage.py makemigrations
  python manage.py migrate
  ```

#### Register Model in `admin.py`
```python
from django.contrib import admin
from .models import Product
admin.site.register(Product)
```

#### Serialize the Model (`serializers.py`)
```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

#### Create API Views (`views.py`)
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

#### Define URLs (`urls.py` in `appname`)
```python
from django.urls import path
from .views import product_list

urlpatterns = [
    path('products/', product_list, name='product-list'),
]
```

#### Register API Routes in Project `urls.py`
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('appname.urls')),  # Include API URLs
]
```

---

### Notes
- Adjust file names and paths as per your project structure.
- The API endpoints can be tested using **Postman** or **Django Admin Panel**.
- Django REST API helps in building **scalable web services** efficiently.

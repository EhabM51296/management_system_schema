# management_system_schema

## Overview
-This project purpose is for managing data for users, whatever there system modeling is.
-It allow users to create/edit/delete and read data created/inserted by them.
-Users can create data with the apis created by using data as fields in the api request or by importing a csv file.
-This system needs enhancement to test all cases since we have many scenarios we need to test specially when creating models.
-Such as relations between models and delete records or tables related to each other on cascade

## Setup Instructions
### Create a virtual environment
-python -m venv venv  
-cd to source of venv/bin/activate
.\venv\Scripts\activate



1. **Clone the Repository:**
   ```bash
   git clone https://github.com/EhabM51296/management_system_schema.git
   cd repository
2. **connect to database in the settings.py**
3. **python manage.py makemigrations**
4. **python manage.py migrate**
5. **python manage.py runserver**

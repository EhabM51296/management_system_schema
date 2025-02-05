# management_system_schema

# Overview
-This project purpose is for managing data for users, whatever there system modeling is.
-It allow users to create/edit/delete and read data created/inserted by them.
-Users can create data with the apis created by using data as fields in the api request or by importing a csv file.
-This system needs enhancement to test all cases since we have many scenarios we need to test specially when creating models.
-Such as relations between models and delete records or tables related to each other on cascade

# Setup Instructions
## Create a virtual environment
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


# Adjustment and enhancement
1. **Testing all cases a user may face and adjust solutions and validatoins accordingly**
2. **add error handling system, so whenever an error is faced is saved as log so the user can view errors that he is facing, since this system is based on data, so all data missed must be known and validated specially when we have large data**

# Future Features 
1. **Integrate AI model that lets the user to tell the AI what is the model needed to creare a specific structure for a system, and after the AI created the structure, let the user to decide where to insert that strucure or no to his system**

# Challenegs faced
1. **Valdating different scenarios when creating model or data**


# META API course - final project: an API for the LittleLemon restaurant 

##Short description

This project provides a fully functional API for a small restaurant. It includes basic CRUD capabilities as well as pagination, search & filter functionality, group permissions, token authentication and throttling. The project uses the Django Rest Framework (DRF) as its base and a SQLite3 database.

##Functionality

The project provides support for users (and user groups), a list of menu items, a cart for customers, and order management endpoints which display information for customers, drivers and managers. 

The project uses Token Authentication and makes use of Djoser to provide a wide range of authentication endpoints. More infromation can be found at https://djoser.readthedocs.io/en/latest/getting_started.html#available-endpoints

The project provides three main permission groups: customers, delivery crew (drivers) and manager, as well as admin. HTTP methods and views are restricted appropriately for each group.


##Project files

LittleLemon (main folder)  
---LittleLemon (project folder)  
---LittleLemonAPI (app folder)  

##Installation
You can install the project by using the following:
```
pipenv install 
```
##API Endpoints

TBD




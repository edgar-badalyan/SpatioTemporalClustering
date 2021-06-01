# SpatioTemporalClustering
An attempt to give a spatio-temporal visualisation of coronavirus cases. Data used is from January 2021, in Brussels. Points can be viewed as clusters or individual points.
DBSCAN algorithm is used to compute clusters, and it uses a spatio-temporal distances. The data was randomly generated.

It is also possible to predict the points of Febuary 2021 using SARIMA algorithm.

## Project Structure

The project contains the following files/directories:

* __manage.py__ : main file to run the server 
* __db.sqlite3__ : database with the generated points
* __clustering__ : Django directory with general settings files
* __map__ : 
   * general Django files, including __models.py__, __views.py__, etc
   * __data__ : directory with .csv files used to generate the database
   * __algorithms__ : directory with python files used for DBSCAN clustering, time-series predictions, and point generation
   * __templates__ : HTML templates for the project
   * __static__ : static files (JS/CSS) used with the templates
   * __migrations__ : Django migrations directory


## Configuration 
This tool is built with the following packages, and was tested using the given versions :

* python 3.8.5
* django 2.2.5
* geopy 2.0.0
* numpy 1.19.2
* pandas 1.1.3
* matplotlib 3.3.2
* scikit-learn 0.23.2
* statsmodels 0.12.0
* leaflet 1.7.1
* JQuery 1.12.1
* Bootstrap 4.0.0


## Execution 

To run the project, one can go in directory /clustering and execute:

```bash
python manage.py runserver
```

and then navigate either through the interface or the search bar.

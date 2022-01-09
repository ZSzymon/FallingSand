## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Usage](#usage)
* [Mouse actions](#mouse-actions)

## General info
This project is simple falling sand simulator created by Żywko Szymon.
	
## Technologies

Project is created with:
* PyQt5: 5.15.6
* QDarkStyle: 3.0.3
* numpy
	
## Setup
###Clone this project:

```
$ git clone <url> FallingSand
```
### Create virtual env
```
$ cd FallingSand
$ virtualenv env
$ source env/bin/activate
```

### Install
```
$ pip install -r requirements.txt
```
### Run
```
$ python main.py
```

## Usage

* Known Patterns - Select ready simulations.
* Sand Generate Type - Combo box for choosing sand generation method. 
* Generate - generates sand with chosen method.   
* Play-Pause - Start, stop simulation toogle button.
* Reset - Reset the simulation
* Speed - slider changing simulation speed.
* Next step / Prev step - force next or previous step in simulation.


## Mouse actions
* My recommendation is to use 'empty pattern '
* Left mouse click/move - Remove walls from the pattern.
* Right mouse click/move - Add walls to the pattern.
# MOH Sample Template Conversion Project

This is a small project for converting MOH sample submission templates to the Freezeman sample submission template format.


## Running The App

---
### Streamlit
`streamlit run app_streamlit.py`

---
### CLI
`python -m cli convert <MOH file path>`

*or*

`python -m cli convert <MOH file path> --output_path <FMS file path>`

---
### API

`uvicorn api:app --reload`

> A VSCode launch configuration is also configured for api and cli.


## Setting up a pyevn virtual environment

* Install pyenv and pyenv-virtualenv (on OSX use brew).
* Install the version of Python you want to use:

    `pyenv install 3.8.13`

* Open a terminal and cd to the project directory.

* Choose your python version: 
    
    `pyenv local 3.8.13`

* Create a pyenv virtual environment:

    `pyenv virtualenv 3.8.13 .env_3_8_13`

* Set this as the environment to use in the project directory:

    `pyenv local .env_3_8_13`
* Activate and deactivate your virtual environment with:

    `pyenv activate .env_3_8_13`
    `pyenv deactivate .env_3_8_13`

[How to guide](https://towardsdatascience.com/python-how-to-create-a-clean-learning-environment-with-pyenv-pyenv-virtualenv-pipx-ed17fbd9b790)


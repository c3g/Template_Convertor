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


from io import BytesIO
from pathlib import PurePath
from typing import Union

from fastapi import FastAPI, File
from fastapi.responses import HTMLResponse
from common import FMS_SUBMISSION_TEMPLATE_PATH

from convertor import MOHSampleManifestConversion

"""
    REST API

    
"""


app = FastAPI()

@app.get('/')
def read_root():
    return {"hello": "world"}

@app.get('/items/{item_id}')
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post('/convert/')
def convert_template(filename: str = "output", template: bytes = File()):
    """
    Convert an MOH template to freezeman and return the resulting file.

    The POST request body must include a form, and the MOH upload file must
    be specified in the form with the key `template`.

    The freezeman template is returned as a file download response.
    The log is not returned.

    TODO Figure out the best way to return the fms file and the log -
    either zip them to create a single response, or return the log, 
    cache the converted file, and provide a second end-point to get the converted file.
    """
    fms_template_file_path = PurePath(FMS_SUBMISSION_TEMPLATE_PATH)
    output_file_name = PurePath(filename or 'output').stem + ".fms" + ".xlsx"

    output_file = BytesIO()

    conversion = MOHSampleManifestConversion(
        template, fms_template_file_path, output_file
    )
    conversion.do_conversion()

        # We can't use FastApi's FileResponse because it wants a file path as a parameter and the
    # output template is in a byte stream, not on disk. Instead, we have to use
    # an HTMLResponse and set the headers with the file name.
    return HTMLResponse(
        content = output_file.getvalue(), 
        status_code=200, 
        headers={
            "Content-Type": "application/octet-stream",
            "Content-Disposition": f"attachment; filename={output_file_name}"
        },
        media_type='application/octet-stream',
    )


   



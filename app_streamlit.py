from dataclasses import dataclass
from io import BytesIO
from lib2to3.pytree import convert
from pathlib import PurePath
from typing import BinaryIO, Optional
import streamlit as st
from os.path import splitext
from common import FMS_SUBMISSION_TEMPLATE_PATH
from convertor import MOHSampleManifestConversion
from convertor.core.conversion_log import ConversionLog
from convertor.freezeman import freezeman_template
from version import CONVERTOR_VERSION
import logging


# Set the dom document title. 
# Note: the page config needs to be the first streamlit command used by the app.
st.set_page_config(page_title="Freezeman MGC Template Convertor")

@dataclass
class ConversionState:
    uploaded_template: Optional[BinaryIO] = None
    freezeman_template: Optional[BinaryIO] = None
    freezeman_template_name: Optional[str] = None
    conversion_log: Optional[ConversionLog] = None
    conversion_error: Optional[Exception] = None

    def reset(self):
        self.uploaded_template = None
        self.freezeman_template = None
        self.freezeman_template_name = None
        self.conversion_log = None
        self.conversion_error = None

# Initialize the session state if this is the first run of the script
if 'conversion_state' not in st.session_state:
    st.session_state.conversion_state = ConversionState()

# Create a variable for the conversion_state for code readability    
state = st.session_state.conversion_state

# Callback for file upload
def handle_upload():

    try:
        # Get the uploaded file from the file_uploaded widget and set it in the session state
        state.uploaded_template = st.session_state.file_uploader
    
        # Do the conversion, outputing to a BytesIO stream
        freezeman_template = PurePath(FMS_SUBMISSION_TEMPLATE_PATH)
        output_stream = BytesIO()

        # Write the file name to console to keep track of user activity
        logging.info(f"Converting file: {state.uploaded_template.name}")

        convertor = MOHSampleManifestConversion(state.uploaded_template, freezeman_template, output_stream)
        convertor.do_conversion()

        # Compute a file name for the resulting freezeman template file
        converted_file_name, _ = splitext(state.uploaded_template.name)
        converted_file_name = converted_file_name + '.fms.xlsx'

        # Set the converted state
        state.freezeman_template = output_stream
        state.freezeman_template_name = converted_file_name
        state.conversion_log = convertor.log
        state.conversion_error = None

        logging.info("done")
        
    except Exception as e:
        logging.error(f"An error occured during conversion: ", e)
        state.conversion_error = e


# Reset to upload another file
def reset():
    state.reset()



    
# Components
st.title('Freezeman MGC Template Converter')
st.caption(f'Version: {CONVERTOR_VERSION}')

if state.uploaded_template is None:
    # Display the file upload widget if no template has been uploaded yet.
    st.file_uploader('Select an MOH template', type=['xlsx'], key='file_uploader', accept_multiple_files=False, on_change=handle_upload)
elif state.conversion_error is not None:
    # If conversion failed, display the exception
    st.error(f'File conversion failed')
     # display a reset button to go back to upload state
    st.button('Convert another file', on_click=reset)
    # display the exception
    st.exception(state.conversion_error)
elif state.freezeman_template is not None and state.conversion_log is not None:
    # display a success message
    if state.conversion_log.has_errors_or_warnings():
        st.warning(f'{state.uploaded_template.name} was converted but has errors or warnings')
    else:
         st.success(f'{state.uploaded_template.name} was converted successfully')

    # Display a centered download button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        pass
    with col2:
        # display a download button for the converted file
        FILE_EMOJI = '📄'   # unicode U+1F4C4
        st.download_button(
            f'{FILE_EMOJI} Download {state.freezeman_template_name}', 
            data=state.freezeman_template, 
            file_name=state.freezeman_template_name, 
            help='Click to download the converted file')
    with col3:
        pass

    # with col1:
    #     # display a download button for the converted file
    #     st.download_button(f'Download {state.freezeman_template_name}', data=state.freezeman_template, file_name=state.freezeman_template_name, help='Click to download the converted file')
    # with col2:
    #     # display a reset button to go back to upload state
    #     st.button('Convert another file', on_click=reset, help='Click to upload another file')

    # display a reset button to go back to upload state
    st.button('Convert another file', on_click=reset, help='Click to upload another file')

    # list log errors and warnings
    st.subheader('Messages')

    with st.container():
        for msg in state.conversion_log.general_messages:
            st.caption(msg)
        st.caption('Note that even if problems or warnings appear below, you can still download the template and correct problems manually.')
        for row_number, row_messages in state.conversion_log.row_messages.items():
            for error_message in row_messages['errors']:
                st.text(f'PROBLEM Row {row_number}: {error_message}')
            for warning_message in row_messages['warnings']:
                st.text(f'WARNING Row {row_number}: {warning_message}')




    
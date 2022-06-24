from io import BytesIO
from lib2to3.pytree import convert
from pathlib import PurePath
import streamlit as st
from os.path import splitext
from convertor import MOHSampleManifestConversion


# Set up session state
if 'uploaded_template' not in st.session_state:
    st.session_state.uploaded_template = None

if 'converted' not in st.session_state:
    st.session_state.converted = None


# Callback for file upload
def handle_upload():

    try:
        # Get the uploaded file and set it in the session state
        st.session_state.uploaded_template = st.session_state.file_uploader
    
        # Do the conversion, outputing to a BytesIO stream
        freezeman_template = PurePath("config/fms_sample_submission_template.xlsx")
        output_stream = BytesIO()

        convertor = MOHSampleManifestConversion(st.session_state.uploaded_template, freezeman_template, output_stream)
        convertor.do_conversion()

        # Compute a file name for the resulting freezeman template file
        converted_file_name, _ = splitext(st.session_state.uploaded_template.name)
        converted_file_name = converted_file_name + '.fms.xlsx'

        # Set the converted state
        st.session_state.converted = dict(
            file = output_stream,
            name = converted_file_name,
            log = convertor.log
        )
    except Exception as e:
        # TODO Display an error banner
        pass


# Reset to upload another file
def reset():
    st.session_state.uploaded_template = None
    st.session_state.converted = None
    
# Components
st.title('Freezeman MGC Template Converter')

if st.session_state.uploaded_template is None:
    uploaded_file = st.file_uploader('Select an MOH template', type=['xlsx'], key='file_uploader', accept_multiple_files=False, on_change=handle_upload)
elif st.session_state.converted is not None:
    st.success('File converted successfully')
    # display a download button for the converted file
    if st.session_state.converted['file']:
        st.download_button(f'Download {st.session_state.converted["name"]}', data=st.session_state.converted['file'], file_name=st.session_state.converted["name"])
    else:
        st.write('File conversion failed')

    # TODO list errors and warnings
    # list log errors and warnings

else:
    st.text(f'Processing file: {st.session_state.uploaded_template.name}')
    st.spinner('Processing file')

if st.session_state.uploaded_template is not None:
    st.button('Convert another file', on_click=reset)


    
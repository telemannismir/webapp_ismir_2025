import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    layout="wide",
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome 👋")

col1, col2 = st.columns(2, gap="large", border=True)
col1.subheader("Voice annotations")
col2.subheader("Abreviations used")

with col1:
    st.markdown("""
    |annotation|corresponding voice|
    |:----:|:---:|
    |$x$|note with voice annotation|
    |$.$|rest|
    |$u$|upper voice|
    |$b$|bass voice|
    |$B$|opposite stems-notes : bass voice|
    |$m$|middle voice|
 """)


with col2:
        st.markdown("""
    |abbreviations|meaning|
    |:----:|:---:|
    |BM|binary meter|
    |TM|ternary meter|
    |♪♪|group of 2 8th within a same beat in binary|
    |♬♬|group of 4 16th within a same beat in binary|
    |♪♪♪|group of 3 8th within a same beat in ternary|
    """)
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    layout="wide",
    page_title="Hello",
    page_icon="👋",
)

hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)

st.write("# Welcome 👋")

col1, col2 = st.columns(2, gap="large", border=True)
col1.subheader("Presentation")
col2.subheader("Scores")

with col1:
    st.markdown(
        """
    - introduction
    - Glossary of fields
        """
    )


with col2:
    f = st.slider("Choose your fantasia", 1, 12, 1)
    with st.container():
        pdf_viewer(f"scores/Fantasia{f}.pdf")
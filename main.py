import streamlit as st

from forms.kiem_dich import show as show_kiem_dich
from forms.bao_quan import show as show_bao_quan
from forms.execution_followup import show as show_execution_followup
FORMS = {
    "Mẫu CV KIỂM DỊCH ADM":
        show_kiem_dich,

    "Mẫu CV bảo quản hàng":
        show_bao_quan,
    "Mẫu CV UQ DLy KDich ADM":
       show_execution_followup
}

st.set_page_config(
    page_title="ADM Document Generator",
    page_icon= "logo.jpg",
    layout="wide"
)
st.markdown("""
<style>

[data-testid="stSidebar"]{
    background-color:#F5F7FA;
}

.stButton > button{
    background-color:#00A651;
    color:white;
    border-radius:10px;
    height:45px;
    border:none;
    font-weight:600;
}

.stButton > button:hover{
    background-color:#008A43;
    color:white;
}

h1{
    color:#003366;
}

h2{
    color:#003366;
}

.block-container{
    padding-top:2rem;
}

</style>
""", unsafe_allow_html=True)
with st.sidebar:

    st.image(
        "logo.jpg",
        use_container_width=True
    )

    st.markdown(
        "### ADM Document Generator"
    )

    st.markdown("---")

selected_form = st.sidebar.selectbox(
    "Chọn biểu mẫu",
    list(FORMS.keys())
)

FORMS[selected_form]()
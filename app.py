import streamlit as st
import streamlit.components.v1 as components

NIEUW = "https://www.psdnet.nl/vaarstaten/"

st.set_page_config(page_title="Verhuisd naar psdnet.nl/vaarstaten/", page_icon="⚓", layout="centered")

# Automatische doorverwijzing (breekt uit de component-iframe naar het hoofdvenster)
components.html(
    f"""
    <script>
      var url = "{NIEUW}";
      try {{ window.top.location.replace(url); }}
      catch (e) {{ window.parent.location.replace(url); }}
    </script>
    <a href="{NIEUW}" target="_top">Ga verder naar PSDnet.nl</a>
    """,
    height=40,
)

st.title("De vaarstaten zijn verhuisd")
st.write("Deze app is vervangen door de vaarstaten op PSDnet.nl, met per schip een eigen pagina.")
st.link_button("Naar de vaarstaten op PSDnet.nl", NIEUW, type="primary")
st.caption("Word je niet automatisch doorgestuurd? Klik dan op de knop hierboven.")

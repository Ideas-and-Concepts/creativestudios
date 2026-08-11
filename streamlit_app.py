from pathlib import Path
import streamlit as st


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
LOGO_FILE = BASE_DIR / "logo.svg"


# ============================================================
# BUILT-IN CREATIVE STUDIOS LOGO
# ============================================================

CREATIVE_STUDIOS_LOGO = """<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 500 500">

<rect width="500" height="500" rx="90" fill="#050505"/>

<!-- Architectural frame -->
<path
d="M110 365 L110 155 L250 70 L390 155 L390 365"
fill="none"
stroke="#2563EB"
stroke-width="22"
stroke-linejoin="round"/>

<!-- Central structure -->
<path
d="M160 365 L160 205 L250 150 L340 205 L340 365"
fill="none"
stroke="#60A5FA"
stroke-width="18"
stroke-linejoin="round"/>

<!-- Vertical construction lines -->
<path
d="M205 365 L205 235
M250 365 L250 205
M295 365 L295 235"
fill="none"
stroke="#2563EB"
stroke-width="14"/>

<!-- Foundation -->
<path
d="M75 385 H425"
stroke="#FFFFFF"
stroke-width="20"
stroke-linecap="round"/>

<!-- Blue accent -->
<circle
cx="250"
cy="110"
r="18"
fill="#2563EB"/>

</svg>
"""


# ============================================================
# ENSURE LOGO EXISTS
# ============================================================

def ensure_logo():

    try:

        if not LOGO_FILE.exists():

            LOGO_FILE.write_text(
                CREATIVE_STUDIOS_LOGO,
                encoding="utf-8",
            )

        return True

    except Exception:

        return False


# Create the logo before Streamlit tries to display it.
ensure_logo()


# ============================================================
# LOGO DISPLAY
# ============================================================

def render_logo(
    width=120,
):

    """
    Displays the Creative Studios logo.

    Uses the actual logo.svg when available.
    Falls back to the built-in SVG if necessary.
    """

    try:

        if LOGO_FILE.exists():

            st.image(
                str(LOGO_FILE),
                width=width,
            )

            return

    except Exception:
        pass


    # --------------------------------------------------------
    # Guaranteed fallback
    # --------------------------------------------------------

    import base64

    encoded = base64.b64encode(
        CREATIVE_STUDIOS_LOGO.encode(
            "utf-8"
        )
    ).decode(
        "utf-8"
    )


    st.markdown(
        f"""
        <div style="
            width:{width}px;
            height:{width}px;
            margin:0 auto 15px auto;
            display:flex;
            align-items:center;
            justify-content:center;
        ">

            <img
                src="data:image/svg+xml;base64,{encoded}"
                style="
                    width:100%;
                    height:100%;
                    object-fit:contain;
                "
            >

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login_page(
    login_function,
    db,
):

    # --------------------------------------------------------
    # LOGIN CONTAINER
    # --------------------------------------------------------

    left, center, right = st.columns(
        [1, 1.1, 1]
    )


    with center:

        st.markdown(
            """
            <div style="
                height:50px;
            ">
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        render_logo(
            width=125
        )


        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                text-align:center;
                color:#FFFFFF;
                font-size:27px;
                font-weight:850;
                letter-spacing:-0.6px;
                margin-top:5px;
            ">
                Creative Studios
            </div>

            <div style="
                text-align:center;
                color:#60A5FA;
                font-size:10px;
                font-weight:750;
                letter-spacing:1.3px;
                text-transform:uppercase;
                margin-top:6px;
                margin-bottom:28px;
            ">
                AEC Collaboration Platform
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # LOGIN FORM
        # ----------------------------------------------------

        with st.form(
            "creative_studios_login",
            clear_on_submit=False,
        ):

            username = st.text_input(
                "Username",
                placeholder="Enter username",
            )


            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password",
            )


            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )


        if submitted:

            if login_function(
                db,
                username,
                password,
            ):

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )
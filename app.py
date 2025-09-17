import re

import streamlit as st
import streamlit.components.v1 as components

# CSS to hide the top bar and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.session_state["max_soc"] = 100


def get_battery_color(soc):
    """Get battery color based on SOC level."""
    if soc > 75:
        return "#4CAF50"
    if soc > 50:
        return "#FFEB3B"
    if soc > 25:
        return "#FF9800"
    return "#F44336"


def create_battery_component(soc, battery_id, width=180, height=280):
    """Create an HTML component with SVG battery icon."""
    color = get_battery_color(soc)

    # calculate fill height based on SOC (battery body is 120 units tall)
    fill_height = max(3, (soc / 105) * 120)  # Minimum 3 units for visibility
    fill_y = 120 - fill_height  # Start fill from top

    # create HTML with embedded SVG
    html_content = f"""
    <div style="text-align: center; margin: 8px; background: rgba(245, 243, 231, 0.4); border-radius: 12px; padding: 12px; box-shadow: 0 3px 6px rgba(139, 115, 85, 0.1);">
        <h3 style="margin-bottom: 10px; color: #8b7355; font-family: 'Arial', sans-serif;">Battery {battery_id}</h3>
        <svg width="{width}" height="{height - 80}" viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg" style="border: 2px solid #d4c5a9; border-radius: 15px; background: linear-gradient(145deg, #fefdf8, #f5f3e7); box-shadow: inset 0 2px 4px rgba(139, 115, 85, 0.1);">
            <!-- Battery terminal -->
            <rect x="35" y="8" width="30" height="12" fill="#8b7355" rx="4"/>
            
            <!-- Battery body outline -->
            <rect x="15" y="20" width="70" height="120" fill="rgba(254, 253, 248, 0.9)" stroke="#8b7355" stroke-width="3" rx="6"/>
            
            <!-- Battery fill with animation -->
            <rect x="18" y="{17 + fill_y}" width="64" height="{fill_height}" fill="{color}" rx="3" opacity="0.9">
                <animate attributeName="height" 
                         values="0;{fill_height}" 
                         dur="1.2s" 
                         begin="0s"
                         fill="freeze"/>
                <animate attributeName="y" 
                         values="140;{17 + fill_y}" 
                         dur="1.2s" 
                         begin="0s"
                         fill="freeze"/>
            </rect>
            
            <!-- Battery fill highlight -->
            <rect x="20" y="{25 + fill_y}" width="8" height="{max(0, fill_height)}" fill="rgba(255, 255, 255, 0.3)" rx="2" opacity="0.7">
                <animate attributeName="height" 
                         values="0;{max(0, fill_height)}" 
                         dur="1.2s" 
                         begin="0s"
                         fill="freeze"/>
                <animate attributeName="y" 
                         values="140;{25 + fill_y}" 
                         dur="1.2s" 
                         begin="0s"
                         fill="freeze"/>
            </rect>
            
            <!-- SOC percentage text -->
            <text x="50" y="85" text-anchor="middle" fill="#5d4e37" font-size="18" font-weight="bold" font-family="Arial, sans-serif">
                {soc:.0f}%
            </text>
        </svg>
                <div style="margin-top: 10px;">
            <p style="margin: 5px 0; font-weight: bold; color: #8b7355; font-size: 14px;">SOC: {soc}%</p>
        </div>
    </div>
    """

    return html_content


def extract_soc_from_message(message):
    """Extract SOC percentage from user message - just find any number."""
    # Find any number in the message
    numbers = re.findall(r"\d+", message)

    for num_str in numbers:
        num = int(num_str)
        if 0 <= num <= 100:  # Valid SOC range
            return num

    return None


def create_ai_chat_interface(current_soc):
    """Create AI chat interface that extracts SOC values."""
    st.markdown("### 🤖 AI Battery Assistant")

    # chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! What can I do for you today? You can ask me to set the MAX SOC of your batteries.",
            },
        ]

    if "current_soc" not in st.session_state:
        st.session_state.current_soc = 100

    # display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div style="background: rgba(139, 115, 85, 0.1); padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;">
                    <strong>You:</strong> {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div style="background: rgba(245, 243, 231, 0.6); padding: 10px; border-radius: 10px; margin: 5px 0;">
                    <strong>🤖 AI Assistant:</strong> {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

    user_input = st.chat_input("Type your message here...")

    if user_input:
        # add user message to chat and get SoC
        st.session_state.messages.append({"role": "user", "content": user_input})
        extracted_soc = extract_soc_from_message(user_input)

        if extracted_soc is not None:
            st.session_state.current_soc = extracted_soc
            st.session_state.max_soc = extracted_soc  # Update the main SOC value
            response = f"Perfect! I've set the MAX SOC of your batteries to {extracted_soc}%. The batteries are now updating to reflect this change."
        else:
            response = "I understand you want to adjust the battery settings. Please tell me a number between 0-100 for the SOC percentage, like '75' or 'set to 80'."

        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to update the display
        st.rerun()

    return st.session_state.current_soc


def main():
    st.set_page_config(
        page_title="Battery SOC Monitor",
        page_icon="🔋",
        layout="wide",
    )

    st.markdown(
        """
    <style>
    .stApp {
        background-color: #fefdf8;
    }
    .stSlider > div > div > div > div {
        background-color: #f5f3e7;
    }
    .stMarkdown {
        color: #5d4e37;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #8b7355 !important;
    }
    .stColumns {
        background-color: rgba(245, 243, 231, 0.3);
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("🔋 Battery SOC Monitor")
    st.markdown("---")

    # st.markdown("---")

    st.markdown("### AI Battery Fleet Manager")

    # batteries on left, chat on right
    battery_section, chat_section = st.columns([2, 1])

    with chat_section:
        st.session_state.max_soc = create_ai_chat_interface(100)

    with battery_section:
        st.markdown("#### Battery Grid")

        # First row of batteries
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            battery1_html = create_battery_component(st.session_state.max_soc, 1)
            components.html(battery1_html, height=350)
        with row1_col2:
            battery2_html = create_battery_component(st.session_state.max_soc, 2)
            components.html(battery2_html, height=350)

        # Second row of batteries
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            battery3_html = create_battery_component(st.session_state.max_soc, 3)
            components.html(battery3_html, height=350)
        with row2_col2:
            battery4_html = create_battery_component(st.session_state.max_soc, 4)
            components.html(battery4_html, height=350)

    st.markdown("---")


if __name__ == "__main__":
    main()

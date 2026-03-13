import streamlit as st
from utils.rag import generate_eligibility

st.set_page_config(page_title="SwiftVisa AI")

st.title("SwiftVisa: AI-Based Visa Eligibility Screening Agent  ")

st.write("Chat with the assistant to evaluate your visa eligibility.")

# -------------------------
# Session State Initialization
# -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = 0

if "profile" not in st.session_state:
    st.session_state.profile = {}

questions = [
    ("age", "What is your age?"),
    ("nationality", "What is your nationality?"),
    ("education", "What is your highest education level?"),
    ("employment", "What is your current occupation?"),
    ("income", "What is your annual income (USD)?"),
    ("country", "Which country are you applying to?"),
    ("visa_type", "Which visa type are you applying for? (example: h1b)")
]

# -------------------------
# Display Chat History
# -------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# Ask First Question Automatically
# -------------------------

if st.session_state.step == 0 and len(st.session_state.messages) == 0:
    question = questions[0][1]
    st.session_state.messages.append({"role": "assistant", "content": question})
    st.rerun()

# -------------------------
# Chat Input
# -------------------------

user_input = st.chat_input("Type your answer...")

if user_input:

    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    key, _ = questions[st.session_state.step]

    # Save user input
    st.session_state.profile[key] = user_input

    st.session_state.step += 1

    # -------------------------
    # Ask Next Question
    # -------------------------

    if st.session_state.step < len(questions):

        next_question = questions[st.session_state.step][1]

        st.session_state.messages.append(
            {"role": "assistant", "content": next_question}
        )

    # -------------------------
    # All Questions Completed
    # -------------------------

    else:

        with st.spinner("Analyzing visa eligibility..."):

            response, docs = generate_eligibility(
                st.session_state.profile,
                response_mode="concise"
            )

        # Parse structured response
        status = ""
        explanation = ""
        confidence = ""

        for line in response.split("\n"):

            if "Eligibility Status" in line:
                status = line.split(":",1)[1].strip()

            elif "Short Explanation" in line or "Explanation" in line:
                explanation = line.split(":",1)[1].strip()

            elif "Confidence Score" in line:
                confidence = line.split(":",1)[1].strip()

        result_text = f"""
### Eligibility Status:
{status}

### Explanation:
{explanation}

### Confidence Score:
{confidence}
"""

        st.session_state.messages.append(
            {"role": "assistant", "content": result_text}
        )

        # -------------------------
        # Show Retrieved Sources
        # -------------------------

        if docs:

            source_text = "### Retrieved Policy Sources:\n"

            for i, doc in enumerate(docs):

                source_text += f"\n**Source {i+1}:** {doc.metadata.get('source_file','Unknown')}\n"

                source_text += doc.page_content[:300] + "...\n"

            st.session_state.messages.append(
                {"role": "assistant", "content": source_text}
            )

    st.rerun()
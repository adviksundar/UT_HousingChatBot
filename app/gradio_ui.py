import tempfile
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geomapping_retriever import find_apartments
from app.chatbot import chatbot_response
import gradio as gr
import re

# Predefined majors
majors = [
    "Computer Science", "Mechanical Engineering", "Business",
    "Psychology", "Fine Arts", "Biology", "Architecture", "Education"
]

# System prompts
FIRST_RESPONSE_PROMPT = (
    "You are a helpful real estate assistant specializing in finding rental properties for UT Austin students. "
    "You are assisting the student over a full conversation, not just answering one question.\n\n"
    "When responding to the first message:\n"
    "- Start with a friendly greeting (e.g., 'Hi there! I'm happy to help you find housing.').\n"
    "- Suggest up to 3 housing options based on the student's major, budget, and preferences.\n"
    "- Always prioritize listings within the student's budget.\n"
    "- Only suggest listings slightly above the budget if no good options are available.\n"
    "- Present listings as a numbered list (1., 2., 3.).\n"
    "- Bold the name of each apartment or community using **bold markdown formatting**.\n"
    "- Clearly mention the monthly rent for each option.\n"
    "- Keep each suggestion short (1-2 sentences).\n"
    "- If suggesting options above budget, apologize politely and explain why.\n"
    "- End by offering to assist further if needed.\n\n"
    "Context: Maintain full memory of the conversation. Understand and relate each new user message to prior inputs and your prior responses."
)

FOLLOWUP_RESPONSE_PROMPT = (
    "You are a helpful real estate assistant specializing in finding rental properties for UT Austin students. "
    "You have full memory of the conversation. Always relate your new responses to previous user questions and your prior answers.\n\n"
    "When responding to follow-up questions:\n"
    "- Answer naturally based on the previous conversation.\n"
    "- Do not greet again.\n"
    "- Continue being friendly, concise, and professional.\n"
    "- Use a numbered list (1., 2., 3.) and bold apartment names if suggesting listings.\n"
    "- If the question is outside housing, politely steer back to housing."
)

# Validation prompt for input checking
VALIDATION_PROMPT_TEMPLATE = (
    "You are an AI assistant validating user inputs for a real estate conversation.\n"
    "Based on the full conversation history and the latest student message, determine:\n\n"
    "✅ If the message is related to real estate, housing, renting, buying, leasing, "
    "asking for apartment/home specifications, or modifying prior real estate queries, reply only: **valid**.\n\n"
    "❌ If the message is off-topic (e.g., jokes, math, random), reply only: **invalid**.\n\n"
    "Respond strictly with only **valid** or **invalid** — nothing else.\n\n"
    "The student is majoring in {major} and has a rent budget of ${budget}.\n\n"
    "Here is the full conversation history:\n\n{conversation}\n\n"
    "Student's latest message:\n{latest_user_message}"
)

def build_conversation_text(history):
    """Formats full conversation as text for prompting."""
    conversation = ""
    for turn in history:
        role = turn["role"]
        content = turn["content"]
        if role == "user":
            conversation += f"Student: {content}\n"
        else:
            conversation += f"Assistant: {content}\n"
    return conversation

MAJORS_SET = {m.lower(): m for m in majors}          # reuse existing list

def detect_major(text: str):
    """Return canonical major name if present in free text, else None."""
    lowered = text.lower()
    for key in MAJORS_SET:
        # whole-word match to avoid false positives like "art" in "apartment"
        if re.search(rf"\b{re.escape(key)}\b", lowered):
            return MAJORS_SET[key]
    return None

def detect_budget(text: str):
    """
    Return an int like 1200 if the message contains '$1200', '1200/month', etc.
    Accepts 3- or 4-digit numbers in the 300-4000 range.
    """
    m = re.search(r'\$?\s*(\d{3,4})\s*(?:[/\s]?(?:per)?\s*(?:month|mo|rent))?', text, re.I)
    if m:
        val = int(m.group(1))
        if 300 <= val <= 4000:        # sanity range for Austin student housing
            return val
    return None

def user_message_submit(history, user_message,
                        major_state, budget_state,
                        budget_slider):
    if history is None:
        history = []

    # Auto-detect major (only once, or until user overwrites)
    if not major_state:
        maybe_major = detect_major(user_message)
        if maybe_major:
            major_state = maybe_major

    # Auto-detect budget
    maybe_budget = detect_budget(user_message)
    if maybe_budget:
        budget_state = maybe_budget
        # Move the slider knob
        slider_update = gr.update(value=budget_state)
    else:
        slider_update = gr.update()   # no change

    history.append({"role": "user", "content": user_message})

    # 5 outputs: chatbot, cleared textbox, major_state, budget_state, slider_update
    return history, "", major_state, budget_state, slider_update



def validate_user_input(history, major_state, budget):
    """Validate the latest user input using model intelligence."""
    if history.count({"role": "user", "content": history[-1]["content"]}) == 1 and len([h for h in history if h["role"] == "user"]) == 1:
        # First ever user message: trust as valid
        return True

    conversation = build_conversation_text(history[:-1])  # everything except the latest user input
    latest_user_message = history[-1]["content"]
    validation_prompt = VALIDATION_PROMPT_TEMPLATE.format(
        major=major_state,
        budget=budget,
        conversation=conversation,
        latest_user_message=latest_user_message
    )

    validation_response = chatbot_response(validation_prompt).strip().lower()

    if "valid" in validation_response:
        return True
    else:
        return False

def generate_bot_reply(major_state, budget_state, history, first_turn):
    if not history:                           # no user text yet
        return history, first_turn, gr.update(visible=False), major_state, budget_state

    major = major_state or "Undeclared"
    budget = budget_state or 1200

    # --------------  validation block (unchanged)  --------------
    if not validate_user_input(history, major, budget):
        polite_warning = (
            "I'm here to assist you with housing-related questions near UT Austin. "
            "Could you please ask something about apartments, rent, leasing, or living preferences?"
        )
        history.append({"role": "assistant", "content": polite_warning})
        return history, first_turn, gr.update(visible=False), major_state, budget_state
    # -------------------------------------------------------------

    # --------------  NEW: retrieve apartments  -------------------
    retrieval_df = find_apartments(major, budget)
    if not retrieval_df.empty:
        apt_md = apartments_to_md(retrieval_df)
        retrieval_note = (
            "Here are the most relevant nearby listings from my database:\n"
            f"{apt_md}\n\n"
        )
        
        # retrieval_df.to_csv(csv_path, index=False)
        temp_dir  = Path(tempfile.gettempdir())
        # csv_path = "/tmp/nearby_apartments.csv"
        csv_path  = str(temp_dir / "nearby_apartments.csv")
        retrieval_df.to_csv(csv_path, index=False)

    else:
        retrieval_note = ""
        csv_path = None
    # -------------------------------------------------------------

    # build system prompt
    prompt = FIRST_RESPONSE_PROMPT if first_turn else FOLLOWUP_RESPONSE_PROMPT
    first_turn = False

    conversation = build_conversation_text(history)
    full_prompt = (
        f"{prompt}\n\n"
        f"The student is majoring in {major} and has a monthly rent budget of ${budget}.\n\n"
        f"{retrieval_note}"
        f"Here is the full conversation so far:\n{conversation}"
    )

    bot_reply = chatbot_response(full_prompt)
    # prepend note only when it’s non-empty
    user_facing_reply = retrieval_note + bot_reply if retrieval_note else bot_reply
    history.append({"role": "assistant", "content": user_facing_reply})

    file_update = gr.update(value=csv_path, visible=bool(csv_path))
    return history, first_turn, file_update, major_state, budget_state


def apartments_to_md(df):
    """
    1. **Address (first line)** – 3 bd / 2 ba • $2800/mo • 0.7 km away
    """
    bullets = []
    for i, row in df.iterrows():
        addr = str(row["address"]).split(",")[0]
        bullets.append(
            f"{i+1}. **{addr}** – "
            f"{row.get('bedrooms','?')} bd / {row.get('bathrooms','?')} ba • "
            f"{row['price']} • {row['average_distance_km']:.2f} km away"
        )
    return "\n".join(bullets)

with gr.Blocks(title="🏡 UT Austin Housing Chatbot") as demo:
    gr.Markdown("# 🏡 UT Austin Housing Chatbot")
    gr.Markdown("Welcome! Set your major and budget, then chat naturally to get rental suggestions.")

    chatbot = gr.Chatbot(
        label="🏡 Chat History",
        height=500,
        type="messages",
        show_copy_button=True,
    )

    retrieval_file = gr.File(label="📄 Download full match list", visible=False)

    major_display = gr.Textbox(
    label="🎓 Detected Major (edit if wrong)",
    value="",
    interactive=True
    )


    with gr.Row():
    #   major = gr.Dropdown(choices=majors, label="🎓 Select your Major", value="Computer Science")
        budget_slider = gr.Slider(500, 2500, step=100, value=1200, label="💰 Monthly Rent Budget ($)")

    message = gr.Textbox(
        placeholder="Type your housing question or preferences here...",
        label="✏️ Your Message",
        lines=2,
        autofocus=True
    )

    with gr.Row():
        submit_btn = gr.Button("💬 Submit")
        clear_btn = gr.Button("🧹 Clear Chat")

    history = gr.State([])
    first_turn = gr.State(True)
    major_state = gr.State("")
    budget_state = gr.State(1200)

    submit_btn.click(
    fn=user_message_submit,
    inputs=[history, message, major_state, budget_state, budget_slider],
    outputs=[chatbot, message, major_state, budget_state, budget_slider],
    ).then(
    fn=generate_bot_reply,
    inputs=[major_state, budget_state, history, first_turn],
    outputs=[chatbot, first_turn, retrieval_file, major_state, budget_state],
    )

    clear_btn.click(
    lambda: ([], True, "", "", 1200, gr.Slider.update(value=1200)),
    None,
    [chatbot, first_turn, message, major_state, budget_state, budget_slider]
    )



demo.launch(debug=False)

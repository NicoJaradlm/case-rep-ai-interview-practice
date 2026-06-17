import json
import time
import random


import streamlit as st

from streamlit_autorefresh import st_autorefresh
from llm_client import call_claude
from prompts import CASE_GENERATION_PROMPT, GRADING_PROMPT
from storage import save_attempt, load_attempts


CASE_TYPES = [
    "Total cost of ownership",
    "Breakeven",
    "Market sizing",
    "Capacity and utilization",
    "Investment decision",
    "Pricing and profitability",
]

INDUSTRIES = [
    "Aviation",
    "Energy",
    "Logistics",
    "Retail",
    "SaaS",
    "Manufacturing",
    "Healthcare",
    "Food and beverage",
    "Real estate",
    "Sports business",
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]


st.set_page_config(
    page_title="CaseRep",
    layout="wide"
)

st.title("CaseRep")
st.caption("10-minute case interview practice for business, strategy, finance, energy, and analytics roles.")

def display_timer(remaining_seconds: float):
    remaining_seconds = max(0, int(remaining_seconds))
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    if remaining_seconds <= 0:
        st.error("Time remaining: 0:00 — Time is up.")
    elif remaining_seconds <= 60:
        st.warning(f"Time remaining: {minutes}:{seconds:02d}")
    else:
        st.success(f"Time remaining: {minutes}:{seconds:02d}")
def submit_answer_for_feedback(case_data, clarification, answer, auto_submitted=False):
    if auto_submitted and not answer.strip():
        answer = "[No answer was submitted before the timer expired.]"

    if auto_submitted:
        answer = f"[AUTO-SUBMITTED WHEN TIMER EXPIRED]\n\n{answer}"

    grading_prompt = GRADING_PROMPT.format(
        case_json=json.dumps(case_data, indent=2),
        clarification=clarification,
        answer=answer,
    )

    feedback = call_claude(grading_prompt)
    st.session_state.feedback = feedback

    save_attempt(
        case_data=case_data,
        clarification=clarification,
        answer=answer,
        feedback=feedback,
    )

    st.session_state.timer_running = False
    st.session_state.case_started = False
    st.session_state.start_time = None
    st.session_state.auto_submitted = auto_submitted
  
def clear_text_inputs():
    for key in ["answer_box", "clarification_box"]:
        if key in st.session_state:
            del st.session_state[key]   
            
def init_state():
    defaults = {
        "case_data": None,
        "case_started": False,
        "start_time": None,
        "feedback": None,
        "auto_submitted": False,
        "timer_running": False,
        "case_type": "Total cost of ownership",
        "industry": "Aviation",
        "difficulty": "Medium",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def extract_json_from_response(raw_text: str) -> dict:
    """
    Claude sometimes returns JSON wrapped in markdown fences or with extra text.
    This function extracts the JSON object safely.
    """
    cleaned = raw_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        json_str = cleaned[start:end + 1]
        return json.loads(json_str)

    raise ValueError("Could not extract valid JSON from Claude response.")


def generate_case(case_type, industry, difficulty):
    prompt = CASE_GENERATION_PROMPT.format(
        case_type=case_type,
        industry=industry,
        difficulty=difficulty,
    )

    raw = call_claude(prompt)

    try:
        return extract_json_from_response(raw)
    except Exception:
        st.error("Claude returned a response that could not be parsed as JSON.")
        st.write("Raw response:")
        st.code(raw)

        return {
            "title": "Parsing Error",
            "case_type": case_type,
            "industry": industry,
            "initial_prompt": "The model returned invalid JSON. Try generating a new case.",
            "ideal_information_to_request": [],
            "data_table": {"columns": [], "rows": []},
            "question_to_solve": "",
            "relevant_data": [],
            "irrelevant_or_optional_data": [],
            "expected_formula": "",
            "step_by_step_solution": [],
            "final_recommendation": "",
            "caveats": [],
            "common_mistakes": [],
        }


def format_table(data_table):
    columns = data_table.get("columns", [])
    rows = data_table.get("rows", [])

    if not columns or not rows:
        return None

    return [dict(zip(columns, row)) for row in rows]



def reset_case():
    clear_text_inputs()
    st.session_state.case_data = None
    st.session_state.case_started = False
    st.session_state.start_time = None
    st.session_state.feedback = None
    st.session_state.timer_running = False
    st.session_state.auto_submitted = False

init_state()


with st.sidebar:
    st.header("Case settings")

    if st.button("Randomize settings", key="btn_randomize_settings"):
        st.session_state.case_type = random.choice(CASE_TYPES)
        st.session_state.industry = random.choice(INDUSTRIES)
        st.session_state.difficulty = random.choice(DIFFICULTIES)
        st.rerun()

    case_type = st.selectbox(
        "Case type",
        CASE_TYPES,
        key="case_type",
    )

    industry = st.selectbox(
        "Industry/context",
        INDUSTRIES,
        key="industry",
    )

    difficulty = st.selectbox(
        "Difficulty",
        DIFFICULTIES,
        key="difficulty",
    )

    st.divider()

    if st.button("Generate new case", key="btn_generate_new_case"):
        with st.spinner("Generating case..."):
            clear_text_inputs()
            st.session_state.case_data = generate_case(case_type, industry, difficulty)
            st.session_state.case_started = False
            st.session_state.start_time = None
            st.session_state.feedback = None
            st.session_state.timer_running = False
            st.session_state.auto_submitted = False
    if st.button("Reset current case", key="btn_reset_current_case"):
        
        reset_case()
        st.rerun()
case_data = st.session_state.case_data

if not case_data:
    st.info("Generate a new case from the sidebar.")
    st.stop()


st.subheader(case_data.get("title", "Case"))

st.markdown("## 1. Initial prompt")
st.write(case_data.get("initial_prompt", ""))

st.markdown("## 2. What information would you ask for?")
clarification = st.text_area(
    "Write the information you would request before solving:",
    height=120,
    placeholder=(
        "Example: I would ask for purchase price, maintenance cost, "
        "operating cost per hour, revenue per hour, utilization, time horizon, "
        "and residual value."
    ),
    key="clarification_box",
)

if st.button("Reveal data and start 10-minute timer", key="btn_reveal_data"):
    st.session_state.case_started = True
    st.session_state.timer_running = True
    st.session_state.start_time = time.time()
    st.session_state.feedback = None
    st.session_state.auto_submitted = False
    st.rerun()
    
if st.session_state.case_started:
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    st.markdown("## 3. Case data")

    table = format_table(case_data.get("data_table", {}))

    if table:
        st.table(table)
    else:
        st.write(case_data.get("data_table", ""))

    st.markdown("## 4. Solve")

    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, 600 - elapsed)

    if st.session_state.timer_running and st.session_state.feedback is None:
        st_autorefresh(interval=1000, key="timer_refresh")

    display_timer(remaining)

    st.write(case_data.get("question_to_solve", ""))

    answer = st.text_area(
        "Your answer:",
        height=260,
        placeholder="Write your formula, calculations, recommendation, and caveats.",
        key="answer_box",
        disabled=remaining <= 0,
    )

    if remaining <= 0 and not st.session_state.auto_submitted:
        st.session_state.timer_running = False

        with st.spinner("Time is up. Auto-submitting and grading your answer..."):
            submit_answer_for_feedback(
                case_data=case_data,
                clarification=clarification,
                answer=st.session_state.get("answer_box", ""),
                auto_submitted=True,
            )

        st.rerun()

    if st.button("Submit answer for feedback", key="btn_submit_answer"):
        current_answer = st.session_state.get("answer_box", "")

        if not current_answer.strip():
            st.error("Write an answer before submitting.")
        else:
            st.session_state.timer_running = False

            with st.spinner("Grading answer..."):
                submit_answer_for_feedback(
                    case_data=case_data,
                    clarification=clarification,
                    answer=current_answer,
                    auto_submitted=False,
                )

            st.rerun()

if st.session_state.feedback:
    st.markdown("## 5. Feedback")
    st.write(st.session_state.feedback)

    with st.expander("Show hidden solution"):
        st.markdown("### Relevant data")
        for item in case_data.get("relevant_data", []):
            st.write(f"- {item}")

        st.markdown("### Irrelevant or optional data")
        for item in case_data.get("irrelevant_or_optional_data", []):
            st.write(f"- {item}")

        st.markdown("### Expected formula")
        st.write(case_data.get("expected_formula", ""))

        st.markdown("### Step-by-step solution")
        for step in case_data.get("step_by_step_solution", []):
            st.write(f"- {step}")

        st.markdown("### Final recommendation")
        st.write(case_data.get("final_recommendation", ""))

        st.markdown("### Caveats")
        for caveat in case_data.get("caveats", []):
            st.write(f"- {caveat}")


with st.expander("Attempt history"):
    attempts = load_attempts()
    st.write(f"Total attempts: {len(attempts)}")

    for attempt in reversed(attempts[-5:]):
        st.write("---")
        st.write(attempt["timestamp"])
        st.write(attempt["case"].get("title", "Untitled case"))
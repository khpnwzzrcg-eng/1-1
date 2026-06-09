import streamlit as st
from google import genai

# ---------------------------
# 페이지 설정
# ---------------------------
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💖",
    layout="centered"
)

st.title("💖 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# ---------------------------
# API 키 확인
# ---------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("GOOGLE_API_KEY가 Secrets에 설정되지 않았습니다.")
    st.stop()

# ---------------------------
# Gemini 클라이언트
# ---------------------------
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 초기화 실패: {e}")
    st.stop()

# ---------------------------
# 채팅 기록 저장
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요! 💖\n\n"
                "연애, 썸, 이별, 재회, 고백, 인간관계 고민을 편하게 이야기해 주세요."
            )
        }
    ]

# 이전 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# 사용자 입력
# ---------------------------
prompt = st.chat_input("고민을 입력하세요...")

if prompt:
    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 대화 기록 생성
        history_text = ""

        for msg in st.session_state.messages:
            role = "사용자" if msg["role"] == "user" else "상담사"
            history_text += f"{role}: {msg['content']}\n"

        system_prompt = """
당신은 따뜻하고 공감 능력이 높은 연애상담 전문가입니다.

규칙:
1. 상대를 존중하는 방향으로 조언한다.
2. 단정적인 판단을 하지 않는다.
3. 공감 → 분석 → 조언 순서로 답변한다.
4. 한국어로 답변한다.
5. 지나친 비난이나 공격을 유도하지 않는다.
"""

        full_prompt = f"""
{system_prompt}

대화 기록:
{history_text}

최신 사용자 메시지:
{prompt}
"""

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=full_prompt
                )

                answer = response.text

                st.markdown(answer)

        # 응답 저장
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except Exception as e:
        error_msg = (
            "죄송합니다. 답변 생성 중 오류가 발생했습니다.\n\n"
            f"오류 내용: {str(e)}"
        )

        with st.chat_message("assistant"):
            st.error(error_msg)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_msg
            }
        )

# ---------------------------
# 사이드바
# ---------------------------
with st.sidebar:
    st.header("설정")

    if st.button("대화 초기화"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "안녕하세요! 💖\n\n"
                    "연애 고민을 편하게 이야기해 주세요."
                )
            }
        ]
        st.rerun()

    st.info(
        "Gemini 2.5 Flash Lite\n"
        "Streamlit Community Cloud 배포용"
    )

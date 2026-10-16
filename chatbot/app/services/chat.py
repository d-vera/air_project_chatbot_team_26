from typing import Optional
from fastapi import HTTPException, status
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.services.upstream import BadGatewayException, UpstreamClient
from app.tools.air_quality import create_air_quality_tools


def build_system_prompt(language: str, first_name: Optional[str] = None) -> str:
    lang_upper = (language or "EN").upper()
    if lang_upper == "ES":
        greeting = (
            f"El nombre del usuario es '{first_name}'. Salúdalo cordialmente por su nombre al inicio de tu respuesta (por ejemplo: 'Hola {first_name}, ...')."
            if first_name
            else "Saluda cordialmente al usuario al inicio de tu respuesta."
        )
        lang_instruction = "Debes responder completamente en Español."
    else:
        greeting = (
            f"The user's first name is '{first_name}'. Greet them warmly by their name at the very beginning of your response (for example: 'Hi {first_name}, ...')."
            if first_name
            else "Greet the user politely at the beginning of your response."
        )
        lang_instruction = "You must respond entirely in English."

    return f"""You are the official Air Project AI Assistant.
You provide users with accurate air quality and environmental measurements (temperature, humidity, CO2, PM1.0, PM2.5, PM10) using your available tools.

Guidelines:
1. {greeting}
2. {lang_instruction}
3. ONLY use the data returned by your tools. NEVER fabricate, assume, or hallucinate measurements or device statistics. If data is unavailable, state so clearly.
4. You have read-only access. You cannot perform modifications or access sensor administration.
5. Provide clear, concise, and helpful answers.
"""


def get_llm():
    settings = get_settings()
    api_key = settings.effective_llm_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": "LLM API key is not configured (set DEEPSEEK_API_KEY or LLM_API_KEY).",
            },
        )
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=api_key,
        base_url=settings.llm_base_url,
        temperature=0.2,
    )


async def process_chat_message(
    message: str,
    token: str,
    language: str = "EN",
    first_name: Optional[str] = None,
    upstream_client: Optional[UpstreamClient] = None,
) -> str:
    """Run the LangChain agent on the message with the provided JWT token context."""
    client = upstream_client or UpstreamClient()
    tools = create_air_quality_tools(token, client)
    system_prompt = build_system_prompt(language, first_name)

    try:
        llm = get_llm()
        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
        )
        result = await agent.ainvoke({"messages": [{"role": "user", "content": message}]})
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            content = getattr(last_msg, "content", "")
            if isinstance(content, list):
                reply = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )
            else:
                reply = str(content)
        else:
            reply = ""
        return reply
    except BadGatewayException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": f"An unexpected error occurred while processing your request: {str(e)}",
            },
        ) from e

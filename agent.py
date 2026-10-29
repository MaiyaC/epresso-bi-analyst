import json
import os
import pandas as pd
from google import genai
from google.genai import types

from analytics import (
    get_revenue_by_channel,
    get_category_performance,
    get_monthly_revenue_share,
    get_store_trend,
    get_data_quality_report,
)


ANALYTICAL_FUNCTIONS = {
    "get_revenue_by_channel": get_revenue_by_channel,
    "get_category_performance": get_category_performance,
    "get_monthly_revenue_share": get_monthly_revenue_share,
    "get_store_trend": get_store_trend,
    "get_data_quality_report": get_data_quality_report,
}

TOOL_DESCRIPTIONS = {
    "get_revenue_by_channel": "Compare revenue and revenue share by sales channel.",
    "get_category_performance": "Analyze revenue and revenue share by product category.",
    "get_monthly_revenue_share": "Analyze monthly revenue as a percentage of each year's revenue.",
    "get_store_trend": "Analyze annual revenue trends for physical stores.",
    "get_data_quality_report": "Check missing values and duplicate Sales IDs.",
}

SYSTEM_INSTRUCTIONS = """
You are the E-Presso Business Intelligence AI Analyst.

Use only the provided analytical tool results for numerical claims.
Never invent revenue, percentages, growth rates, or other statistics.
Never execute arbitrary Python or SQL.
Never describe revenue as profit.
Never claim that a correlation proves causation.

For each answer:
1. Identify the business question.
2. Present calculated facts with relevant numbers.
3. Explain which analytical function and calculation were used.
4. Clearly separate interpretation or recommendations from facts.
5. State relevant limitations or missing data.

Use only the supplied dataset.
Do not claim to have analyzed data that was not provided.
If a question cannot be answered with the available functions,
explain the limitation rather than guessing.
"""


def _json_safe(value):
    """Convert common pandas and NumPy values into JSON-compatible data."""
    return json.loads(
        json.dumps(value, default=lambda x: (
            x.item() if hasattr(x, "item")
            else x.isoformat() if hasattr(x, "isoformat")
            else str(x)
        ))
    )


def answer_business_question(question, data, api_key):
    """Ask Gemini to select an approved analytical function."""

    if not question or not question.strip():
        return {
            "answer": "Please enter a business question.",
            "tool_log": [],
        }

    if not api_key:
        return {
            "answer": "The AI service is not configured. Please contact the dashboard administrator.",
            "tool_log": [],
        }

    if data is None or data.empty:
        return {
            "answer": "There is no loaded sales data available for analysis.",
            "tool_log": [],
        }

    tool_log = []

    try:
        client = genai.Client(api_key=api_key)

        tool_list = [
            types.FunctionDeclaration(
                name=name,
                description=description,
                parameters={
                    "type": "OBJECT",
                    "properties": {},
                },
            )
            for name, description in TOOL_DESCRIPTIONS.items()
        ]

        selection = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=(
                    SYSTEM_INSTRUCTIONS
                    + "\nChoose an approved analytical function when the "
                      "question can be answered by one. "
                      "Otherwise explain the limitation."
                ),
                tools=[types.Tool(function_declarations=tool_list)],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
                temperature=0,
            ),
        )

        calls = selection.function_calls or []

        if not calls:
            return {
                "answer": (
                    selection.text
                    or "This question cannot be answered with the available analytical functions."
                ),
                "tool_log": [],
            }

        tool_responses = []

        for call in calls:
            name = call.name

            if name not in ANALYTICAL_FUNCTIONS:
                return {
                    "answer": "The AI requested an unsupported analytical function.",
                    "tool_log": tool_log,
                }

            result = _json_safe(ANALYTICAL_FUNCTIONS[name](data))

            tool_log.append({
                "function": name,
                "arguments": {},
                "raw_result": result,
            })

            tool_responses.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": result},
                )
            )

        final_response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=question)],
                ),
                selection.candidates[0].content,
                types.Content(
                    role="tool",
                    parts=tool_responses,
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTIONS,
                temperature=0,
            ),
        )

        return {
            "answer": (
                final_response.text
                or "The analytical function ran, but no explanation was returned."
            ),
            "tool_log": tool_log,
        }

    except Exception as error:
        return {
            "answer": (
                "The AI service is temporarily unavailable. "
                "Please try again later. No analytical results were invented."
            ),
            "tool_log": tool_log,
            "error_type": type(error).__name__,
            "error_details": str(error),
        }




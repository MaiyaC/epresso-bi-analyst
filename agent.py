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
    get_customer_satisfaction_analysis,
)

ANALYTICAL_FUNCTIONS = {
    "get_revenue_by_channel": get_revenue_by_channel,
    "get_category_performance": get_category_performance,
    "get_monthly_revenue_share": get_monthly_revenue_share,
    "get_store_trend": get_store_trend,
    "get_data_quality_report": get_data_quality_report,
    "get_customer_satisfaction_analysis": get_customer_satisfaction_analysis,
}

TOOL_DESCRIPTIONS = {
    "get_revenue_by_channel": "Compare revenue and revenue share by sales channel.",
    "get_category_performance": "Analyze revenue and revenue share by product category.",
    "get_monthly_revenue_share": "Analyze monthly revenue as a percentage of each year's revenue.",
    "get_store_trend": "Analyze annual revenue trends for physical stores.",
    "get_data_quality_report": "Check missing values and duplicate Sales IDs.",
    "get_customer_satisfaction_analysis": (
    "Compare customer satisfaction scores with annual physical-store "
    "revenue by matching Store ID and Year. Report observed patterns "
    "without claiming causation."
),
}

SYSTEM_INSTRUCTIONS = """
You are the E-Presso Business Intelligence AI Analyst.

ACCURACY RULES:
- Use only actual results returned by approved analytical functions for numerical claims.
- Never invent revenue, percentages, growth rates, comparisons, or other statistics.
- Never execute arbitrary Python or SQL.
- Never describe revenue as profit.
- Never claim that correlation proves causation.
- Do not invent explanations for trends, such as holidays, customer preferences, marketing campaigns, or operational problems.
- Clearly identify possible explanations as hypotheses that require further investigation.
- Do not claim that data is unavailable simply because the selected function did not analyze it.
- Distinguish between missing data and information that has not yet been analyzed.
- Do not claim to have performed calculations or comparisons that are absent from the tool results.
When describing trends over time, distinguish between an overall
change across the full period and changes in individual years.
Do not describe a trend as continuous or uninterrupted if any
intermediate period shows a reversal.
For example, if revenue declines overall but increases in one year,
describe it as an overall decline with a temporary increase.
Do not use headings such as "Continuous Decline" or
"Uninterrupted Decline" when any store has a year-over-year
increase. Use "Overall Decline with Exceptions" instead.

DATASET CONTEXT:
- The E-Presso dataset includes transaction dates, product categories, sales channels, stores, and revenue.
- Some City values may be missing because Website transactions do not have an associated physical store location.
- Do not assume every missing City value is an error.
- Only state exact missing-value counts or their distribution when confirmed by analytical results.
- Revenue comparisons do not establish profitability because cost and profit-margin information is unavailable.
- The application also uploads a Survey dataset containing Store ID,
  Year, Satisfaction, and Interest fields.
- Survey records are at the store-year level, not the individual
  sales-transaction level.
- Some survey values may be missing. Do not treat missing satisfaction
  scores as zero.
- Customer satisfaction can be analyzed using the approved
  get_customer_satisfaction_analysis function.
- Comparing satisfaction and revenue does not establish that
  satisfaction causes revenue changes.


FOR EACH ANSWER:
1. Identify the business question and relevant scope.
2. Use analytical function results to support all numerical findings.
3. Format the final response using exactly these three main section headings, written in Markdown:
   ### Findings
   Present calculated facts, numerical results, and the analytical function used.

   ### Interpretation
   Explain what the findings mean, including relevant assumptions, limitations, and missing information.

   ### Next Steps
   Provide practical recommendations or identify what additional information is needed.

   Use these exact heading names instead of alternative titles. Do not add other main section headings.
4. Clearly distinguish calculated facts from interpretation and recommendations.
5. Do not invent results or conclusions that are unsupported by the available data.

RECOMMENDATIONS:
- Base recommendations on the actual analytical findings.
- Present recommendations as actions to consider or investigate, not guaranteed solutions.
- Do not recommend operational changes without acknowledging relevant missing information.
- If the available data does not support a recommendation, say so.

Use only the supplied dataset and approved analytical functions.
If a question cannot be answered reliably, explain the limitation
rather than guessing.

RESPONSE FORMATTING RULES:
- Format currency clearly, such as $467,010 or $51,650.
- Format percentages consistently, such as 2.33% or 33.43%.
- Use clean Markdown headings and bullet points.
- Do not include stray symbols, broken Markdown, or malformed text.
- Keep numbers and store IDs together in readable sentences.
- Check the final response for formatting errors before returning it.
- Write currency amounts with a dollar sign and comma separators, such as $529,260.
- Do not place Markdown asterisks inside or immediately next to currency amounts.
- Use plain text for numerical comparisons, such as "Revenue declined from $529,260 to $467,010."
- Do not use bold or italic formatting within sentences containing numerical comparisons.
- Before returning the answer, check that every currency amount displays correctly and that no stray asterisks appear.
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


def answer_business_question(question, data, api_key, survey=None):
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
            "error_type": "MissingAPIKey",
        }

    if data is None or data.empty:
        return {
            "answer": "There is no loaded sales data available for analysis.",
            "tool_log": [],
            "error_type": "MissingData",
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
            model="gemini-3-flash-preview",
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

            if name == "get_customer_satisfaction_analysis":
                if survey is None or survey.empty:
                    result = {
                        "status": "insufficient_data",
                        "message": "No Survey dataset is available for satisfaction analysis."
                    }
                else:
                    result = _json_safe(
                        get_customer_satisfaction_analysis(data, survey)
                    )
            else:
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
            model="gemini-3-flash-preview",
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




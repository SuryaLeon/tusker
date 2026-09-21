import json

from agent.ollama_client import (
    OllamaClient,
)

from agent.tools import (
    generate_schedule,
    get_candidate_rankings,
    get_pair_statistics,
    get_poc_statistics,
    get_schedule,
)


SYSTEM_PROMPT = """
You are a scheduling assistant.

You manage a deterministic POC rotation scheduler.

IMPORTANT RULES:

1. You do NOT calculate schedules yourself.
2. You do NOT invent POC assignments.
3. You do NOT invent statistics.
4. Scheduling calculations must be performed
   using one of the provided Python tools.
5. Your role is to understand the user's request,
   select the correct tool, and explain the result.

Available tools:

generate_schedule
    Generate the schedule and save schedule.xlsx.

get_schedule
    Calculate and return the current schedule.

get_poc_statistics
    Return assignment counts for each POC.

get_pair_statistics
    Return assignment counts for POC pairs.

get_candidate_rankings
    Return candidate pair rankings used by
    the scheduler.

When a tool is required, respond ONLY with JSON:

{
    "action": "tool",
    "tool": "<tool_name>"
}

If no tool is required, respond ONLY with JSON:

{
    "action": "respond",
    "message": "<response>"
}

Do not wrap JSON in markdown.
"""


TOOLS = {
    "generate_schedule":
        generate_schedule,

    "get_schedule":
        get_schedule,

    "get_poc_statistics":
        get_poc_statistics,

    "get_pair_statistics":
        get_pair_statistics,

    "get_candidate_rankings":
        get_candidate_rankings,
}


class SchedulingAgent:
    def __init__(self):
        self.llm = OllamaClient()

    def _ask_llm(
        self,
        user_message,
    ):
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        return self.llm.chat(
            messages
        )

    def _explain_tool_result(
        self,
        original_request,
        tool_name,
        result,
    ):
        prompt = f"""
The user asked:

{original_request}

Python executed this tool:

{tool_name}

The deterministic scheduler returned:

{json.dumps(result, default=str)}

Explain the result clearly and concisely.

Do not invent facts.
Do not change assignments.
Do not recalculate scores.
"""

        messages = [
            {
                "role": "system",
                "content": (
                    "You explain deterministic "
                    "scheduler results. "
                    "Never invent scheduler data."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        return self.llm.chat(
            messages
        )

    def run(
        self,
        user_message,
    ):
        response = self._ask_llm(
            user_message
        )

        try:
            decision = json.loads(
                response
            )

        except json.JSONDecodeError:
            return (
                "Agent returned invalid JSON:\n\n"
                + response
            )

        action = decision.get(
            "action"
        )

        if action == "respond":
            return decision.get(
                "message",
                "",
            )

        if action != "tool":
            return (
                "Unknown agent action: "
                f"{action}"
            )

        tool_name = decision.get(
            "tool"
        )

        tool = TOOLS.get(
            tool_name
        )

        if tool is None:
            return (
                "Agent requested an "
                f"unknown tool: {tool_name}"
            )

        result = tool()

        return self._explain_tool_result(
            original_request=user_message,
            tool_name=tool_name,
            result=result,
        )
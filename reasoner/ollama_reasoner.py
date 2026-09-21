from ollama import Client

from config import (
    ENABLE_AI_REASONING,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


class OllamaReasoner:
    def __init__(self):
        self.enabled = ENABLE_AI_REASONING

        self.client = Client(
            host=OLLAMA_BASE_URL
        )

        self.model = OLLAMA_MODEL

    def health_check(self) -> bool:
        if not self.enabled:
            return False

        try:
            self.client.list()
            return True

        except Exception:
            return False

    def explain_assignment(
        self,
        assignment,
    ):
        """
        Explain an assignment already made by Python.

        Ollama MUST NOT determine or modify the pair.
        """

        if not self.enabled:
            return self._fallback_reason(
                assignment
            )

        prompt = f"""
You are explaining a scheduling decision already made by
a deterministic Python scheduling algorithm.

You MUST NOT change the assignment.
You MUST NOT recalculate the score.
You MUST NOT invent additional data.

Task table:
{assignment['Table']}

Task:
{assignment['Task']}

Selected POCs:
{assignment['POC1']} and {assignment['POC2']}

Calculated score:
{assignment['Score']}

Historical pair count:
{assignment.get('HistoricalPairCount', 0)}

POC1 previous assignment count:
{assignment.get('POC1AssignmentCount', 0)}

POC2 previous assignment count:
{assignment.get('POC2AssignmentCount', 0)}

Same-table pair count:
{assignment.get('SameTablePairCount', 0)}

Explain in no more than 2 sentences why this was a
reasonable least-repetition assignment.

Only explain the supplied facts.
"""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                options={
                    "temperature": 0,
                },
            )

            return (
                response.message.content
                .strip()
            )

        except Exception as exc:
            print(
                "WARNING: Ollama reasoning failed:"
            )

            print(exc)

            return self._fallback_reason(
                assignment
            )

    @staticmethod
    def _fallback_reason(
        assignment,
    ):
        return (
            "Selected by the deterministic "
            "least-repetition scheduling algorithm "
            f"with score {assignment['Score']}."
        )
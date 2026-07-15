"""
Prompt templates for meeting summarization.
Anti-hallucination guardrails included.
"""

SYSTEM_PROMPT = """You are a precise meeting summarization assistant.

RULES:
1. ONLY use information explicitly stated in the transcript.
2. NEVER fabricate, infer, or assume information not present.
3. If something is unclear or not mentioned, state "Not Mentioned".
4. Be concise and factual.
5. Return ONLY valid JSON — no markdown, no code fences, no extra text."""


SUMMARIZATION_PROMPT = """Analyze the following meeting transcript and produce a structured summary.

Return ONLY a valid JSON object with this exact structure:
{{
    "executive_summary": "A concise 2-4 sentence overview of the meeting's purpose and outcomes.",
    "key_points": [
        "Key point 1",
        "Key point 2"
    ],
    "decisions": [
        "Decision 1",
        "Decision 2"
    ],
    "action_items": [
        {{
            "description": "What needs to be done",
            "assignee": "Person responsible (or 'Not Mentioned')",
            "priority": "high/medium/low",
            "due_date": "YYYY-MM-DD or null"
        }}
    ],
    "keywords": [
        "keyword1",
        "keyword2"
    ]
}}

IMPORTANT:
- If no decisions were made, return an empty list for "decisions".
- If no action items were identified, return an empty list for "action_items".
- Extract 5-10 meaningful keywords/topics.
- For action items, only include items that were explicitly discussed.
- Set priority based on urgency discussed in the meeting.
- If an assignee is not mentioned, use "Not Mentioned".

TRANSCRIPT:
{transcript}"""


EXECUTIVE_SUMMARY_PROMPT = """Write a concise 2-4 sentence executive summary of this meeting transcript.
Focus on: the purpose of the meeting, key outcomes, and any major decisions.
Only use information from the transcript. If something is unclear, state that.

TRANSCRIPT:
{transcript}"""

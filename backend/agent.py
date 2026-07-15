from typing import Any, Dict, List, Tuple

TOOL_NAMES = [
    'Summarize from Voice Note',
    'Recommend next best action',
    'Suggest follow-up timing',
    'Prepare account plan',
    'Draft outreach email',
]


def summarize_hcp_profile(submission: Dict[str, Any], message: str, mode: str) -> Tuple[str, List[str]]:
    hcp = submission.get('hcpName', 'the HCP')
    topics = submission.get('topicsDiscussed', 'general engagement')
    sentiment = submission.get('hcpSentiment', 'Neutral')
    reply = f"[Summarize] Summary for {hcp}: Key topics covered include {topics}. HCP sentiment was {sentiment}. Strong foundation for follow-up engagement."
    suggestions = [
        'Schedule a 30-minute follow-up call within 2 weeks',
        'Prepare value-added clinical data relevant to discussed topics',
        'Consider sending a brief email summary within 24 hours',
    ]
    return reply, suggestions


def recommend_next_best_action(submission: Dict[str, Any], message: str, mode: str) -> Tuple[str, List[str]]:
    outcomes = submission.get('outcomes', 'no specific outcomes')
    sentiment = submission.get('hcpSentiment', 'Neutral')
    if sentiment == 'Positive':
        action = "proceed with product education materials and schedule follow-up"
    elif sentiment == 'Negative':
        action = "address concerns before follow-up and gather more information"
    else:
        action = "continue relationship building with targeted value proposition"
    reply = f"[Next Action] Based on the interaction, recommended action: {action}. Outcomes recorded: {outcomes}."
    suggestions = [
        'Send thank you email with key takeaways',
        'Share clinical evidence relevant to discussion',
        'Set a reminder to follow up in 2 weeks',
    ]
    return reply, suggestions


def suggest_follow_up_timing(submission: Dict[str, Any], message: str, mode: str) -> Tuple[str, List[str]]:
    reply = "[Timing] Recommended follow-up timing: 48-72 hours for initial touchpoint, then a substantive follow-up within 2 weeks. This maintains engagement momentum while allowing time for preparation."
    suggestions = [
        'Send brief follow-up message within 48 hours',
        'Schedule main follow-up meeting within 2 weeks',
        'Mark calendar for third touch-point in 1 month',
    ]
    return reply, suggestions


def prepare_account_plan(submission: Dict[str, Any], message: str, mode: str) -> Tuple[str, List[str]]:
    reply = "[Account Plan] Account plan prepared with focus on: (1) value-based education, (2) one tailored clinical proposition, (3) one clear call-to-action. Review outcomes and suggested follow-ups to refine strategy."
    suggestions = [
        'Identify 2-3 key clinical topics for future engagement',
        'Prepare a 1-page value proposition document',
        'Plan next interaction with specific agenda items',
    ]
    return reply, suggestions


def draft_outreach_email(submission: Dict[str, Any], message: str, mode: str) -> Tuple[str, List[str]]:
    hcp = submission.get('hcpName', 'the HCP')
    topics = submission.get('topicsDiscussed', 'our discussion')
    reply = f"[Email Draft] Dear {hcp}, Thank you for your time discussing {topics}. I appreciated your insights and would like to share some additional clinical evidence relevant to our conversation. Available for a brief call next week if helpful. Best regards."
    suggestions = [
        'Customize email with specific clinical references',
        'Attach one relevant clinical resource',
        'Include 2-3 time slots for follow-up call',
    ]
    return reply, suggestions


def route_tool(tool_name: str, submission: Dict[str, Any], message: str, mode: str) -> Tuple[str, List[str]]:
    tool_map = {
        'Summarize from Voice Note': summarize_hcp_profile,
        'Recommend next best action': recommend_next_best_action,
        'Suggest follow-up timing': suggest_follow_up_timing,
        'Prepare account plan': prepare_account_plan,
        'Draft outreach email': draft_outreach_email,
    }
    handler = tool_map.get(tool_name, summarize_hcp_profile)
    return handler(submission, message, mode)

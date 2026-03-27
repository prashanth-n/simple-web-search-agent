from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings
from app.db.models import GenericResearchRun, MarketingAnalysisRun, StartupAnalysisRun


@dataclass(frozen=True)
class AgentProfile:
    id: int
    slug: str
    name: str
    description: str
    system_prompt: str
    model: str
    run_model: type


DEFAULT_MODEL = get_settings().ollama_model

AGENT_PROFILES: dict[int, AgentProfile] = {
    1: AgentProfile(
        id=1,
        slug="generic_web_research",
        name="Generic Web Research",
        description=(
            "Finds, reads, and summarizes credible web sources for broad research queries."
        ),
        system_prompt=(
            "You are a neutral web research analyst. Prioritize factual synthesis, cite only "
            "what is supported by the source content, and keep summaries concise."
        ),
        model=DEFAULT_MODEL,
        run_model=GenericResearchRun,
    ),
    2: AgentProfile(
        id=2,
        slug="startup_analyst",
        name="Startup Analyst",
        description=(
            "Evaluates markets, competitors, positioning, risks, and opportunities for startup "
            "or venture-style questions."
        ),
        system_prompt=(
            "You are a startup analyst. Summaries should focus on market signals, product "
            "positioning, competition, growth opportunities, and execution risks."
        ),
        model=DEFAULT_MODEL,
        run_model=StartupAnalysisRun,
    ),
    3: AgentProfile(
        id=3,
        slug="marketing_analyst",
        name="Marketing Analyst",
        description=(
            "Extracts messaging, audience insights, channel ideas, and brand or campaign "
            "takeaways from web content."
        ),
        system_prompt=(
            "You are a marketing analyst. Summaries should emphasize target audience, "
            "messaging, channel strategy, differentiation, and campaign insights."
        ),
        model=DEFAULT_MODEL,
        run_model=MarketingAnalysisRun,
    ),
}


def get_agent_profile(agent_id: int) -> AgentProfile | None:
    return AGENT_PROFILES.get(agent_id)


def list_agent_profiles() -> list[AgentProfile]:
    return list(AGENT_PROFILES.values())

from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings
from app.db.models import (
    FinancialAnalysisRun,
    GenericResearchRun,
    MarketingAnalysisRun,
    ProductCompetitorAnalysisRun,
    StartupAnalysisRun,
)


@dataclass(frozen=True)
class AgentProfile:
    id: int
    slug: str
    name: str
    description: str
    system_prompt: str
    model: str
    run_model: type
    mode: str


DEFAULT_MODEL = get_settings().ollama_model

AGENT_PROFILES: dict[int, AgentProfile] = {
    1: AgentProfile(
        id=1,
        slug="generic_web_research",
        name="Generic Web Research",
        description="Finds, reads, and summarizes credible web sources for broad research queries.",
        system_prompt=(
            "You are a neutral web research analyst. Prioritize factual synthesis, cite only "
            "what is supported by the source content, and keep summaries concise."
        ),
        model=DEFAULT_MODEL,
        run_model=GenericResearchRun,
        mode="research",
    ),
    2: AgentProfile(
        id=2,
        slug="startup_analyst",
        name="Startup Analyst",
        description="Evaluates markets, competitors, positioning, risks, and opportunities for startup or venture-style questions.",
        system_prompt=(
            "You are a startup analyst. Summaries should focus on market signals, product "
            "positioning, competition, growth opportunities, and execution risks."
        ),
        model=DEFAULT_MODEL,
        run_model=StartupAnalysisRun,
        mode="research",
    ),
    3: AgentProfile(
        id=3,
        slug="marketing_analyst",
        name="Marketing Analyst",
        description="Extracts messaging, audience insights, channel ideas, and brand or campaign takeaways from web content.",
        system_prompt=(
            "You are a marketing analyst. Summaries should emphasize target audience, "
            "messaging, channel strategy, differentiation, and campaign insights."
        ),
        model=DEFAULT_MODEL,
        run_model=MarketingAnalysisRun,
        mode="research",
    ),
    4: AgentProfile(
        id=4,
        slug="product_competitor_analysis",
        name="Product Competitor Analysis",
        description="Compares products, identifies direct and indirect competitors, and explains differentiation, gaps, and strategic risks.",
        system_prompt=(
            "You are a product competitor analyst. Focus on competitive set, positioning, "
            "differentiation, feature gaps, pricing cues, and go-to-market implications."
        ),
        model=DEFAULT_MODEL,
        run_model=ProductCompetitorAnalysisRun,
        mode="competitor",
    ),
    5: AgentProfile(
        id=5,
        slug="financial_analyst",
        name="Financial Analyst",
        description="Explains stock price trends, company snapshots, and basic fundamentals with a chart-ready financial payload.",
        system_prompt=(
            "You are a financial analyst. Explain market data clearly, avoid speculation, and "
            "base summaries on the supplied company snapshot and price series."
        ),
        model=DEFAULT_MODEL,
        run_model=FinancialAnalysisRun,
        mode="financial",
    ),
}


def get_agent_profile(agent_id: int) -> AgentProfile | None:
    return AGENT_PROFILES.get(agent_id)


def list_agent_profiles() -> list[AgentProfile]:
    return list(AGENT_PROFILES.values())

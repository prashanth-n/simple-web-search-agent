import { useMemo, useState } from "react";
import { Bot, ExternalLink, Search as SearchIcon, Sparkles } from "lucide-react";

import { useAgents } from "@/hooks/use-agents";
import { useResearch } from "@/hooks/use-research";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Input } from "./ui/input";
import { Select } from "./ui/select";

export default function Search() {
  const [query, setQuery] = useState("");
  const [manualAgentId, setManualAgentId] = useState("");
  const { agents, isLoading: loadingAgents, errorMessage: agentsError } = useAgents();
  const {
    runResearch,
    results,
    isLoading: loadingResearch,
    errorMessage: researchError,
    resetResearch,
  } = useResearch();

  const selectedAgentId = manualAgentId || (agents[0] ? String(agents[0].id) : "");
  const error = researchError || agentsError;

  const selectedAgent = useMemo(
    () => agents.find((agent) => String(agent.id) === selectedAgentId) ?? null,
    [agents, selectedAgentId],
  );
  const placeholder = useMemo(() => {
    switch (selectedAgent?.slug) {
      case "startup_analyst":
        return "Analyze B2B fintech startup opportunities in Southeast Asia";
      case "marketing_analyst":
        return "Find messaging and channel ideas for an AI note-taking product";
      case "generic_web_research":
        return "Research AI infrastructure startup trends in Europe";
      default:
        return "Ask this agent to research a topic";
    }
  }, [selectedAgent]);

  async function handleResearch(event) {
    event.preventDefault();
    if (!query.trim() || !selectedAgentId) {
      return;
    }

    try {
      await runResearch({ query: query.trim(), agentId: selectedAgentId });
    } catch {
      // Error state is surfaced from the hook.
    }
  }

  const handleAgenctChange = (event) => {
    setManualAgentId(event.target.value);
    setQuery("");
    resetResearch()
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-4 py-6 md:px-6 lg:flex-row lg:py-10">
      <aside className="w-full lg:max-w-sm">
        <Card className="overflow-hidden border-white/60 bg-card/95">
          <CardHeader className="gap-4 border-b border-border/70 bg-card/80">
            <Badge>Agent Control</Badge>
            <div className="space-y-2">
              <CardTitle className="text-3xl">Web Research MCP</CardTitle>
              <CardDescription className="text-sm leading-6">
                Pick an agent, understand its role, then run focused web research from one
                workspace.
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="space-y-3">
              <label className="text-sm font-semibold text-foreground">Agent</label>
              <Select
                disabled={loadingAgents}
                value={selectedAgentId}
                onChange={(event) => {handleAgenctChange(event)}}
              >
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))}
              </Select>
            </div>

            <Card className="border-border/70 bg-secondary/50 shadow-none">
              <CardContent className="space-y-3 p-5">
                <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                  <Bot className="h-4 w-4" />
                  What this agent does
                </div>
                <p className="text-sm leading-6 text-muted-foreground">
                  {selectedAgent?.description ||
                    "Loading the selected agent description from the backend."}
                </p>
              </CardContent>
            </Card>

            <div className="rounded-2xl border border-border/70 bg-card/70 p-5">
              <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
                <Sparkles className="h-4 w-4 text-accent" />
                Included agents
              </div>
              <div className="space-y-2 text-sm text-muted-foreground">
                {agents.map((agent) => (
                  <div key={agent.id} className="rounded-xl bg-background/70 px-3 py-2">
                    {agent.name}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </aside>

      <section className="min-w-0 flex-1">
        <div className="grid gap-6">
          <Card className="border-white/60 bg-card/95">
            <CardHeader className="gap-4">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                  <SearchIcon className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>Research workspace</CardTitle>
                  <CardDescription className="mt-1">
                    Search, scrape, and summarize the web with the currently selected agent.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <form className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto]" onSubmit={handleResearch}>
                <Input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder={placeholder}
                />
                <Button
                  disabled={loadingResearch || loadingAgents || !selectedAgentId}
                  size="lg"
                  type="submit"
                >
                  {loadingResearch ? "Researching..." : "Research"}
                </Button>
              </form>

              {error ? (
                <p className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                  {error}
                </p>
              ) : null}
            </CardContent>
          </Card>

          <div className="grid gap-4">
            {results.length === 0 ? (
              <Card className="border-dashed border-border/80 bg-card/70">
                <CardContent className="flex min-h-56 flex-col items-center justify-center gap-3 p-8 text-center">
                  <div className="rounded-full bg-primary/10 p-4 text-primary">
                    <SearchIcon className="h-6 w-6" />
                  </div>
                  <h2 className="text-xl font-semibold">No research results yet</h2>
                  <p className="max-w-xl text-sm leading-6 text-muted-foreground">
                    Choose an agent on the left, enter a query, and the backend will fetch web
                    sources, summarize them, and store the run in the matching agent table.
                  </p>
                </CardContent>
              </Card>
            ) : null}

            {results.map((item, index) => (
              <Card key={`${item.source}-${index}`} className="border-white/60 bg-card/95">
                <CardHeader className="gap-3">
                  <div className="flex items-start justify-between gap-4">
                    <CardTitle className="text-2xl leading-8">{item.title}</CardTitle>
                    {selectedAgent ? <Badge className="shrink-0">{selectedAgent.name}</Badge> : null}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm leading-7 text-muted-foreground">{item.summary}</p>
                  <a
                    className="inline-flex items-center gap-2 text-sm font-semibold text-primary transition-colors hover:text-accent"
                    href={item.source}
                    rel="noreferrer"
                    target="_blank"
                  >
                    View source
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

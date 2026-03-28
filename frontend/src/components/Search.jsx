import { useMemo, useState } from "react";
import {
  BarChart3,
  Bot,
  ExternalLink,
  LineChart as LineChartIcon,
  MessagesSquare,
  Plus,
  Search as SearchIcon,
  Sparkles,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useAgents } from "@/hooks/use-agents";
import { useAuthActions } from "@/hooks/use-auth";
import { useCreateThread, useMessages, useSendMessage, useThreadMemory, useThreads } from "@/hooks/use-chat";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Select } from "./ui/select";
import { Textarea } from "./ui/textarea";

function formatDate(dateString) {
  if (!dateString) {
    return "";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(new Date(dateString));
}

function formatNumber(value) {
  if (value === "" || value === null || value === undefined) {
    return "N/A";
  }

  const numeric = Number(value);
  if (Number.isNaN(numeric)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(numeric);
}

function placeholderForAgent(selectedAgent) {
  switch (selectedAgent?.slug) {
    case "startup_analyst":
      return "Which B2B payroll startups are strongest in Southeast Asia, and where are the gaps?";
    case "marketing_analyst":
      return "How are AI note-taking products positioning themselves across creators and teams?";
    case "product_competitor_analysis":
      return "Analyze Notion AI competitors, differentiation, and feature gaps.";
    case "financial_analyst":
      return "Analyze AAPL and explain the recent price trend plus company fundamentals.";
    case "generic_web_research":
      return "Research AI infrastructure startup trends in Europe.";
    default:
      return "Ask this agent a question.";
  }
}

function ResearchAttachment({ metadata }) {
  const results = metadata?.results ?? [];
  const competitors = metadata?.competitors ?? [];
  const sources = metadata?.sources ?? [];

  return (
    <div className="grid gap-3">
      {competitors.length > 0 ? (
        <Card className="border-border/70 bg-secondary/40 shadow-none">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Competitor overview</CardTitle>
            <CardDescription>{metadata.company_or_product}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {competitors.map((competitor, index) => (
              <div key={`${competitor.name}-${index}`} className="rounded-2xl border border-border/70 bg-card/80 p-4">
                <h4 className="font-semibold">{competitor.name}</h4>
                <p className="mt-2 text-sm text-muted-foreground">{competitor.positioning}</p>
                <p className="mt-2 text-sm">
                  <span className="font-semibold">Strengths:</span> {competitor.strengths || "N/A"}
                </p>
                <p className="mt-1 text-sm">
                  <span className="font-semibold">Weaknesses:</span> {competitor.weaknesses || "N/A"}
                </p>
              </div>
            ))}
            {sources.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {sources.map((source) => (
                  <a
                    key={source}
                    className="inline-flex items-center gap-1 rounded-full bg-background/80 px-3 py-1 text-xs font-medium text-primary"
                    href={source}
                    rel="noreferrer"
                    target="_blank"
                  >
                    Source
                    <ExternalLink className="h-3 w-3" />
                  </a>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      {results.map((item, index) => (
        <Card key={`${item.source}-${index}`} className="border-border/70 bg-card/80 shadow-none">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg leading-7">{item.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm leading-6 text-muted-foreground">{item.summary}</p>
            <a
              className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
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
  );
}

function FinancialAttachment({ metadata }) {
  const points = metadata?.chart?.points ?? [];
  const snapshot = metadata?.snapshot ?? {};

  return (
    <div className="grid gap-3 lg:grid-cols-[minmax(0,1.4fr)_minmax(280px,0.8fr)]">
      <Card className="border-border/70 bg-card/80 shadow-none">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <LineChartIcon className="h-4 w-4 text-primary" />
            Price chart
          </CardTitle>
          <CardDescription>{metadata.company || metadata.ticker}</CardDescription>
        </CardHeader>
        <CardContent className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(109, 96, 79, 0.16)" />
              <XAxis dataKey="date" tickFormatter={formatDate} minTickGap={24} />
              <YAxis domain={["auto", "auto"]} tickFormatter={(value) => `$${Number(value).toFixed(0)}`} />
              <Tooltip
                formatter={(value) => [`$${Number(value).toFixed(2)}`, "Close"]}
                labelFormatter={(value) => formatDate(value)}
              />
              <Line
                type="monotone"
                dataKey="close"
                stroke="hsl(var(--primary))"
                strokeWidth={3}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card className="border-border/70 bg-card/80 shadow-none">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="h-4 w-4 text-accent" />
            Company snapshot
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 text-sm">
          <div><span className="font-semibold">Ticker:</span> {metadata.ticker}</div>
          <div><span className="font-semibold">Sector:</span> {snapshot.sector || "N/A"}</div>
          <div><span className="font-semibold">Industry:</span> {snapshot.industry || "N/A"}</div>
          <div><span className="font-semibold">Market cap:</span> {formatNumber(snapshot.market_cap)}</div>
          <div><span className="font-semibold">P/E ratio:</span> {snapshot.pe_ratio || "N/A"}</div>
          <div><span className="font-semibold">Revenue TTM:</span> {formatNumber(snapshot.revenue_ttm)}</div>
          <div><span className="font-semibold">Profit margin:</span> {snapshot.profit_margin || "N/A"}</div>
          <p className="rounded-2xl bg-background/70 p-3 text-muted-foreground">
            {snapshot.description || "No company description returned by the data provider."}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function MessageBubble({ message, selectedAgent }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`flex ${isAssistant ? "justify-start" : "justify-end"}`}>
      <div className={`max-w-4xl ${isAssistant ? "w-full" : "max-w-2xl"}`}>
        <div
          className={`rounded-3xl px-5 py-4 ${
            isAssistant ? "bg-card/95 border border-border/70" : "bg-primary text-primary-foreground"
          }`}
        >
          <div className="mb-2 flex items-center justify-between gap-3">
            <span className={`text-xs font-semibold uppercase tracking-[0.2em] ${isAssistant ? "text-primary" : "text-primary-foreground/80"}`}>
              {isAssistant ? selectedAgent?.name || "Assistant" : "You"}
            </span>
            <span className={`text-xs ${isAssistant ? "text-muted-foreground" : "text-primary-foreground/70"}`}>
              {formatDate(message.created_at)}
            </span>
          </div>
          <p className={`whitespace-pre-wrap text-sm leading-7 ${isAssistant ? "text-foreground" : "text-primary-foreground"}`}>
            {message.content}
          </p>
        </div>

        {isAssistant && message.message_type === "research_results" ? (
          <div className="mt-3">
            <ResearchAttachment metadata={message.metadata} />
          </div>
        ) : null}

        {isAssistant && message.message_type === "financial_snapshot" ? (
          <div className="mt-3">
            <FinancialAttachment metadata={message.metadata} />
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function Search({ user }) {
  const [manualAgentId, setManualAgentId] = useState("");
  const [selectedThreadId, setSelectedThreadId] = useState("");
  const [draft, setDraft] = useState("");

  const { agents, isLoading: loadingAgents, errorMessage: agentsError } = useAgents();
  const selectedAgentId = manualAgentId || (agents[0] ? String(agents[0].id) : "");
  const selectedAgent = useMemo(
    () => agents.find((agent) => String(agent.id) === selectedAgentId) ?? null,
    [agents, selectedAgentId],
  );

  const { threads, isLoading: loadingThreads, errorMessage: threadsError } = useThreads(selectedAgentId);
  const { messages, isLoading: loadingMessages, errorMessage: messagesError } = useMessages(selectedThreadId);
  const { memory, isLoading: loadingMemory, errorMessage: memoryError } = useThreadMemory(selectedThreadId);
  const { createChatThread, isCreating, errorMessage: createThreadError } = useCreateThread();
  const { submitMessage, isSending, errorMessage: sendMessageError } = useSendMessage(selectedAgentId);
  const { logout, isSubmitting: isLoggingOut } = useAuthActions();

  const error = sendMessageError || createThreadError || messagesError || memoryError || threadsError || agentsError;
  const placeholder = placeholderForAgent(selectedAgent);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!draft.trim() || !selectedAgentId) {
      return;
    }

    try {
      let activeThreadId = selectedThreadId;

      if (!activeThreadId) {
        const response = await createChatThread({
          agentId: selectedAgentId,
          title: draft.trim().slice(0, 80),
        });
        activeThreadId = String(response.thread.id);
        setSelectedThreadId(activeThreadId);
      }

      await submitMessage({ threadId: activeThreadId, content: draft.trim() });
      setDraft("");
    } catch {
      // Hook state surfaces the error.
    }
  }

  function handleAgentChange(event) {
    setManualAgentId(event.target.value);
    setSelectedThreadId("");
    setDraft("");
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[1600px] flex-col gap-6 px-4 py-6 md:px-6 lg:grid lg:grid-cols-[320px_320px_minmax(0,1fr)] lg:py-10">
      <aside className="grid gap-6">
        <Card className="overflow-hidden border-white/60 bg-card/95">
          <CardHeader className="gap-4 border-b border-border/70 bg-card/80">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2">
                <Badge>Agent Control</Badge>
                <CardTitle className="text-3xl">Web Research MCP</CardTitle>
                <CardDescription className="text-sm leading-6">
                  Multi-agent chat for research, competitor analysis, and finance.
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold">{user?.display_name || user?.email}</div>
                <div className="text-xs text-muted-foreground">{user?.email}</div>
                <Button
                  className="mt-3"
                  disabled={isLoggingOut}
                  onClick={() => logout()}
                  type="button"
                  variant="secondary"
                >
                  {isLoggingOut ? "Signing out..." : "Log out"}
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="space-y-3">
              <label className="text-sm font-semibold text-foreground">Agent</label>
              <Select disabled={loadingAgents} value={selectedAgentId} onChange={handleAgentChange}>
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
                  {selectedAgent?.description || "Loading the selected agent description from the backend."}
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

      <aside className="grid gap-6">
        <Card className="border-white/60 bg-card/95">
          <CardHeader className="border-b border-border/70 pb-5">
            <div className="flex items-center justify-between gap-3">
              <div>
                <CardTitle className="text-xl">Threads</CardTitle>
                <CardDescription className="mt-1">
                  Persistent conversations for {selectedAgent?.name || "the selected agent"}.
                </CardDescription>
              </div>
              <Button
                size="default"
                variant="secondary"
                onClick={() => {
                  setSelectedThreadId("");
                  setDraft("");
                }}
                type="button"
              >
                <Plus className="mr-2 h-4 w-4" />
                New
              </Button>
            </div>
          </CardHeader>
          <CardContent className="grid gap-3 pt-6">
            {loadingThreads ? <p className="text-sm text-muted-foreground">Loading threads...</p> : null}
            {!loadingThreads && threads.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-border/80 bg-background/60 p-5 text-sm text-muted-foreground">
                No chats yet for this agent. Start a new conversation from the composer.
              </div>
            ) : null}
            {threads.map((thread) => (
              <button
                key={thread.id}
                className={`rounded-2xl border px-4 py-3 text-left transition-colors ${
                  String(thread.id) === selectedThreadId
                    ? "border-primary bg-primary/10"
                    : "border-border/70 bg-card/70 hover:bg-secondary/50"
                }`}
                onClick={() => setSelectedThreadId(String(thread.id))}
                type="button"
              >
                <div className="font-semibold">{thread.title}</div>
                <div className="mt-1 text-xs text-muted-foreground">
                  Updated {formatDate(thread.updated_at)}
                </div>
              </button>
            ))}
          </CardContent>
        </Card>
      </aside>

      <section className="min-w-0">
        <Card className="flex min-h-[80vh] flex-col border-white/60 bg-card/95">
          <CardHeader className="border-b border-border/70">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                <MessagesSquare className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>
                  {selectedThreadId
                    ? threads.find((thread) => String(thread.id) === selectedThreadId)?.title || "Conversation"
                    : "New conversation"}
                </CardTitle>
                <CardDescription className="mt-1">
                  {selectedAgent ? `Chat with ${selectedAgent.name}` : "Select an agent to begin."}
                </CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col gap-4 p-6">
            {selectedThreadId ? (
              <Card className="border-border/70 bg-secondary/40 shadow-none">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg">Thread context</CardTitle>
                  <CardDescription>
                    Auto-saved summary and key facts for this conversation.
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4 text-sm">
                  {loadingMemory ? (
                    <p className="text-muted-foreground">Loading thread context...</p>
                  ) : (
                    <>
                      <div>
                        <div className="mb-2 font-semibold text-foreground">Summary</div>
                        <p className="rounded-2xl bg-background/70 p-4 leading-6 text-muted-foreground">
                          {memory.summary || "No summary saved yet for this thread."}
                        </p>
                      </div>
                      <div>
                        <div className="mb-2 font-semibold text-foreground">Key facts</div>
                        {memory.facts?.length ? (
                          <div className="flex flex-wrap gap-2">
                            {memory.facts.map((fact) => (
                              <Badge key={fact.id} variant="secondary" className="px-3 py-1 text-xs">
                                {fact.metadata?.label ? `${fact.metadata.label}: ` : ""}
                                {fact.metadata?.value || fact.content}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <p className="text-muted-foreground">No structured facts saved yet.</p>
                        )}
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            ) : null}

            <div className="flex-1 space-y-4 overflow-y-auto">
              {selectedThreadId && loadingMessages ? (
                <p className="text-sm text-muted-foreground">Loading messages...</p>
              ) : null}

              {!selectedThreadId && !loadingMessages ? (
                <div className="flex min-h-[420px] flex-col items-center justify-center gap-4 rounded-3xl border border-dashed border-border/80 bg-background/60 p-8 text-center">
                  <div className="rounded-full bg-primary/10 p-4 text-primary">
                    <SearchIcon className="h-6 w-6" />
                  </div>
                  <h2 className="text-2xl font-semibold">Start a new chat</h2>
                  <p className="max-w-2xl text-sm leading-7 text-muted-foreground">
                    Ask for web research, competitor positioning, or a ticker-based financial
                    analysis. A thread will be created automatically when you send the first message.
                  </p>
                </div>
              ) : null}

              {selectedThreadId && messages.length === 0 && !loadingMessages ? (
                <div className="rounded-3xl border border-dashed border-border/80 bg-background/60 p-8 text-center text-sm text-muted-foreground">
                  This thread has no messages yet.
                </div>
              ) : null}

              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} selectedAgent={selectedAgent} />
              ))}
            </div>

            <form className="grid gap-4 border-t border-border/70 pt-4" onSubmit={handleSubmit}>
              <Textarea
                className="min-h-[110px]"
                onChange={(event) => setDraft(event.target.value)}
                placeholder={placeholder}
                value={draft}
              />
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm text-muted-foreground">
                  {selectedAgent?.slug === "financial_analyst"
                    ? "Include a stock ticker symbol, for example AAPL or MSFT."
                    : "The agent will respond with chat text and structured cards when useful."}
                </p>
                <Button
                  disabled={loadingAgents || isCreating || isSending || !selectedAgentId || !draft.trim()}
                  size="lg"
                  type="submit"
                >
                  {isCreating || isSending ? "Sending..." : "Send message"}
                </Button>
              </div>
              {error ? (
                <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                  {error}
                </p>
              ) : null}
            </form>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

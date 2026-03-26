import { useState } from "react";

import { research } from "../lib/api";

function Button({ children, disabled, onClick, type = "button" }) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      style={{
        appearance: "none",
        border: 0,
        borderRadius: 12,
        padding: "0 20px",
        height: 48,
        background: disabled ? "#8eb2aa" : "#1d6f5f",
        color: "#fff",
        fontSize: 15,
        fontWeight: 700,
        cursor: disabled ? "not-allowed" : "pointer",
        boxShadow: "0 12px 24px rgba(29, 111, 95, 0.22)",
      }}
    >
      {children}
    </button>
  );
}

function Input(props) {
  return (
    <input
      {...props}
      style={{
        width: "100%",
        height: 48,
        padding: "0 16px",
        borderRadius: 12,
        border: "1px solid #d9c9ae",
        background: "rgba(255, 250, 242, 0.95)",
        fontSize: 15,
        color: "#1f2933",
        outline: "none",
      }}
    />
  );
}

function Card({ children }) {
  return (
    <article
      style={{
        border: "1px solid #d9c9ae",
        background: "rgba(255, 252, 247, 0.92)",
        borderRadius: 18,
        padding: 20,
        boxShadow: "0 16px 40px rgba(43, 35, 20, 0.08)",
      }}
    >
      {children}
    </article>
  );
}

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleResearch(event) {
    event.preventDefault();
    if (!query.trim()) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      const payload = await research(query.trim());
      setResults(payload.results ?? []);
    } catch (err) {
      setError(err.message || "Request failed");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "48px 20px",
        display: "grid",
        placeItems: "start center",
      }}
    >
      <section
        style={{
          width: "min(960px, 100%)",
          display: "grid",
          gap: 20,
        }}
      >
        <Card>
          <div style={{ display: "grid", gap: 18 }}>
            <div style={{ display: "grid", gap: 8 }}>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 800,
                  letterSpacing: "0.16em",
                  textTransform: "uppercase",
                  color: "#1d6f5f",
                }}
              >
                Web Research MCP
              </span>
              <h1 style={{ margin: 0, fontSize: "clamp(2rem, 4vw, 3.5rem)" }}>
                Search, scrape, and summarize the web.
              </h1>
              <p style={{ margin: 0, color: "#596579", fontSize: 16, lineHeight: 1.6 }}>
                Enter a query and the backend agent will collect source pages, distill them,
                and return structured research summaries.
              </p>
            </div>

            <form
              onSubmit={handleResearch}
              style={{
                display: "grid",
                gap: 12,
                gridTemplateColumns: "minmax(0, 1fr) auto",
              }}
            >
              <Input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Research renewable energy storage trends"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Researching..." : "Research"}
              </Button>
            </form>

            {error ? (
              <p style={{ margin: 0, color: "#b42318", fontWeight: 600 }}>{error}</p>
            ) : null}
          </div>
        </Card>

        <div style={{ display: "grid", gap: 16 }}>
          {results.map((item) => (
            <Card key={item.source}>
              <div style={{ display: "grid", gap: 12 }}>
                <h2 style={{ margin: 0, fontSize: 22 }}>{item.title}</h2>
                <p style={{ margin: 0, color: "#334155", lineHeight: 1.7 }}>{item.summary}</p>
                <a
                  href={item.source}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    color: "#1d6f5f",
                    fontWeight: 700,
                    textDecoration: "none",
                  }}
                >
                  {item.source}
                </a>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </main>
  );
}

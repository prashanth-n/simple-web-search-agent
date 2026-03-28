import { useState } from "react";
import { LockKeyhole, Mail, UserRound } from "lucide-react";

import { useAuthActions } from "@/hooks/use-auth";
import { getGoogleLoginUrl } from "@/lib/api";
import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";

export default function AuthScreen() {
  const [mode, setMode] = useState("login");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { signUp, login, isSubmitting, errorMessage } = useAuthActions();

  async function handleSubmit(event) {
    event.preventDefault();
    if (!email.trim() || !password.trim()) {
      return;
    }

    try {
      if (mode === "signup") {
        await signUp({
          email: email.trim(),
          password,
          display_name: displayName.trim() || email.split("@")[0],
        });
        return;
      }

      await login({ email: email.trim(), password });
    } catch {
      // Error state is surfaced from the hook.
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl items-center px-4 py-8 md:px-6">
      <div className="grid w-full gap-6 lg:grid-cols-[1.2fr_minmax(380px,0.8fr)]">
        <section className="rounded-[2rem] border border-white/60 bg-card/90 p-8 shadow-panel">
          <div className="max-w-xl space-y-6">
            <div className="inline-flex rounded-full bg-secondary px-4 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-primary">
              Private Workspace
            </div>
            <h1 className="text-5xl font-semibold leading-tight">
              Sign in to save chats, agent runs, and financial research by user.
            </h1>
            <p className="text-lg leading-8 text-muted-foreground">
              Authentication adds personal thread history, Google login, and user ownership across every
              research and financial analysis artifact.
            </p>
          </div>
        </section>

        <Card className="border-white/60 bg-card/95">
          <CardHeader className="space-y-3">
            <CardTitle className="text-3xl">{mode === "login" ? "Log in" : "Create account"}</CardTitle>
            <CardDescription>
              {mode === "login"
                ? "Continue with your email and password, or use Google."
                : "Create an account to keep your chats and analyses private."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form className="space-y-4" onSubmit={handleSubmit}>
              {mode === "signup" ? (
                <div className="space-y-2">
                  <label className="text-sm font-medium">Display name</label>
                  <div className="relative">
                    <UserRound className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      className="pl-10"
                      onChange={(event) => setDisplayName(event.target.value)}
                      placeholder="Prashanth"
                      value={displayName}
                    />
                  </div>
                </div>
              ) : null}

              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    className="pl-10"
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="you@example.com"
                    type="email"
                    value={email}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <div className="relative">
                  <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    className="pl-10"
                    minLength={8}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="At least 8 characters"
                    type="password"
                    value={password}
                  />
                </div>
              </div>

              <Button className="w-full" disabled={isSubmitting} size="lg" type="submit">
                {isSubmitting ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
              </Button>
            </form>

            <Button className="w-full" onClick={() => window.location.assign(getGoogleLoginUrl())} size="lg" type="button" variant="secondary">
              Continue with Google
            </Button>

            {errorMessage ? (
              <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                {errorMessage}
              </p>
            ) : null}

            <p className="text-sm text-muted-foreground">
              {mode === "login" ? "New here?" : "Already have an account?"}{" "}
              <button
                className="font-semibold text-primary"
                onClick={() => setMode(mode === "login" ? "signup" : "login")}
                type="button"
              >
                {mode === "login" ? "Create an account" : "Log in"}
              </button>
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

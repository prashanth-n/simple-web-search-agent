import AuthScreen from "./components/AuthScreen";
import Search from "./components/Search";
import { useCurrentUser } from "./hooks/use-auth";

export default function App() {
  const { user, isLoading, isAuthenticated } = useCurrentUser();

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm font-medium text-muted-foreground">Loading workspace...</p>
      </main>
    );
  }

  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  return <Search user={user} />;
}

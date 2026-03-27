import { useQuery } from "@tanstack/react-query";

import { fetchAgents } from "@/lib/api";

export function useAgents() {
  const query = useQuery({
    queryKey: ["agents"],
    queryFn: fetchAgents,
    select: (payload) => payload.agents ?? [],
    staleTime: 5 * 60 * 1000,
  });

  return {
    agents: query.data ?? [],
    isLoading: query.isPending,
    errorMessage: query.error?.message ?? "",
  };
}

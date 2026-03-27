import { useMutation } from "@tanstack/react-query";

import { research } from "@/lib/api";

export function useResearch() {
  const mutation = useMutation({
    mutationFn: ({ query, agentId }) => research(query, agentId),
  });

  return {
    runResearch: mutation.mutateAsync,
    resetResearch: mutation.reset,
    results: mutation.data?.results ?? [],
    isLoading: mutation.isPending,
    errorMessage: mutation.error?.message ?? "",
  };
}

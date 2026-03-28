import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createThread, fetchMessages, fetchThreadMemory, fetchThreads, sendMessage } from "@/lib/api";

export function useThreads(agentId) {
  const query = useQuery({
    queryKey: ["threads", agentId],
    queryFn: () => fetchThreads(agentId),
    select: (payload) => payload.threads ?? [],
    enabled: Boolean(agentId),
  });

  return {
    threads: query.data ?? [],
    isLoading: query.isPending,
    errorMessage: query.error?.message ?? "",
  };
}

export function useMessages(threadId) {
  const query = useQuery({
    queryKey: ["messages", threadId],
    queryFn: () => fetchMessages(threadId),
    select: (payload) => payload.messages ?? [],
    enabled: Boolean(threadId),
  });

  return {
    messages: query.data ?? [],
    isLoading: query.isPending,
    errorMessage: query.error?.message ?? "",
  };
}

export function useThreadMemory(threadId) {
  const query = useQuery({
    queryKey: ["memory", threadId],
    queryFn: () => fetchThreadMemory(threadId),
    select: (payload) => payload.memory ?? { summary: "", facts: [] },
    enabled: Boolean(threadId),
  });

  return {
    memory: query.data ?? { summary: "", facts: [] },
    isLoading: query.isPending,
    errorMessage: query.error?.message ?? "",
  };
}

export function useCreateThread() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({ agentId, title }) => createThread(agentId, title),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["threads", variables.agentId] });
    },
  });

  return {
    createChatThread: mutation.mutateAsync,
    isCreating: mutation.isPending,
    errorMessage: mutation.error?.message ?? "",
  };
}

export function useSendMessage(agentId) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: ({ threadId, content }) => sendMessage(threadId, content),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["messages", variables.threadId] });
      queryClient.invalidateQueries({ queryKey: ["threads", agentId] });
      queryClient.invalidateQueries({ queryKey: ["memory", variables.threadId] });
    },
  });

  return {
    submitMessage: mutation.mutateAsync,
    isSending: mutation.isPending,
    errorMessage: mutation.error?.message ?? "",
  };
}

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { fetchMe, login, logout, signUp } from "@/lib/api";

export function useCurrentUser() {
  const query = useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    retry: false,
  });

  return {
    user: query.data?.user ?? null,
    isLoading: query.isPending,
    isAuthenticated: Boolean(query.data?.user),
    errorMessage: query.error?.message ?? "",
  };
}

export function useAuthActions() {
  const queryClient = useQueryClient();

  const signUpMutation = useMutation({
    mutationFn: signUp,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.setQueryData(["me"], null);
      queryClient.removeQueries({ queryKey: ["threads"] });
      queryClient.removeQueries({ queryKey: ["messages"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  return {
    signUp: signUpMutation.mutateAsync,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    isSubmitting: signUpMutation.isPending || loginMutation.isPending || logoutMutation.isPending,
    errorMessage:
      signUpMutation.error?.message ||
      loginMutation.error?.message ||
      logoutMutation.error?.message ||
      "",
  };
}

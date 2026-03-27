import { cn } from "@/lib/utils";

export function Badge({ className, ...props }) {
  return (
    <div
      className={cn(
        "inline-flex w-fit items-center rounded-full bg-secondary px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-primary",
        className,
      )}
      {...props}
    />
  );
}

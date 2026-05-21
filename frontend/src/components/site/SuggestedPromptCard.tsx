import { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  label: string;
  onClick: () => void;
}

export function SuggestedPromptCard({ icon: Icon, label, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="text-left bg-card border border-border hover:border-primary hover:shadow-sm transition rounded-md p-4 flex items-start gap-3 group"
    >
      <span className="w-9 h-9 rounded-sm bg-accent grid place-items-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition shrink-0">
        <Icon className="w-4 h-4" />
      </span>
      <span className="text-sm text-foreground font-medium leading-snug">{label}</span>
    </button>
  );
}

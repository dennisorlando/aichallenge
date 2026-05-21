import { Bot, User } from "lucide-react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div className={`w-9 h-9 shrink-0 rounded-full grid place-items-center
        ${isUser ? "bg-primary text-primary-foreground" : "bg-accent text-primary border border-border"}`}>
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>
      <div className={`max-w-[78%] rounded-md px-4 py-3 text-sm leading-relaxed border
        ${isUser
          ? "bg-primary text-primary-foreground border-primary rounded-tr-sm"
          : "bg-card text-foreground border-border rounded-tl-sm"}`}>
        <div className={`text-[10px] uppercase tracking-wider font-semibold mb-1 ${isUser ? "opacity-80" : "text-primary"}`}>
          {isUser ? "Tu" : "Assistente Comune di Trento"}
        </div>
        <p className="whitespace-pre-line">{message.content}</p>
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="w-9 h-9 shrink-0 rounded-full grid place-items-center bg-accent text-primary border border-border">
        <Bot className="w-4 h-4" />
      </div>
      <div className="bg-card border border-border rounded-md rounded-tl-sm px-4 py-3 inline-flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-2 h-2 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}

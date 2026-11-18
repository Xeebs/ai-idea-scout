# Scenario 1 — React support widget, Next.js backend, provider stated

## Input

A founder building a Zendesk-alternative support widget hands over:

1. **Composer component source** (React, `ChatComposer.tsx`):

```tsx
export function ChatComposer({ onSend }: { onSend: (text: string) => void }) {
  const [draft, setDraft] = useState("");
  const { messages, setMessages } = useChatStore();

  function handleSend() {
    if (!draft.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text: draft }]);
    onSend(draft);
    setDraft("");
  }

  return (
    <div className="composer">
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

2. Frontend framework: React.
3. Backend runtime: Next.js API routes (App Router).
4. Target provider: Gemini Multimodal Live (explicitly stated).
5. Interaction mode: push-to-talk.
6. Existing auth: a `session` cookie set by their own auth, read on every API route via `getServerSession()`.

## Pass criteria

- [ ] Output states Assumptions with provider = Gemini Multimodal Live and mode = push-to-talk, both marked as *stated*, not defaulted (since both were given).
- [ ] Frontend diff references the real names from the pasted code — `setMessages`, `useChatStore`, the `<button>`/`handleSend` pattern — not generic placeholder names. A mic button is added alongside the existing Send button, not replacing it.
- [ ] The frontend diff's transcript-append step calls `setMessages` the same way `handleSend` already does, so voice turns land as ordinary chat messages.
- [ ] Backend relay stub is written as a Next.js App Router route handler (not a bare Express app), reads the provider API key from an environment variable, and checks the `session` cookie via `getServerSession()`-shaped logic before establishing the outbound connection — mirroring input #6 rather than inventing JWT auth.
- [ ] No provider API key appears anywhere in the frontend code block.
- [ ] Auth handshake paragraph explicitly states the browser never holds the Gemini API key.
- [ ] All three standing risk flags (mic permission/Safari, autoplay policy, continuous-mode cost) are present — even though mode is push-to-talk, the cost flag should still note push-to-talk's lower but nonzero cost rather than being omitted.
- [ ] Manual follow-up checklist includes an environment variable for the Gemini API key and a note that the diff is untested.
- [ ] No instruction to `npm install` any pre-existing "voice composer SDK" package.

## Fail conditions

- Output invents different function/variable names than the pasted code uses.
- Output defaults to OpenAI Realtime despite Gemini being explicitly stated.
- API key appears in any frontend code block.
- Backend stub is a generic Express server unrelated to the stated Next.js App Router runtime.

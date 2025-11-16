"""FastAPI powered GUI for Iron Dillo briefings and LLM chat."""

from __future__ import annotations

import argparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .cli import build_security_brief
from .config import get_settings
from .llm import LLMError, ModernLLMInterface

__all__ = ["app", "main"]

app = FastAPI(title="Iron Dillo Control Room", version="0.2.0")
llm_interface = ModernLLMInterface()


class BriefRequest(BaseModel):
    prompt: str
    audience: str = Field(default="small_businesses")
    topic: str = Field(default="identity")
    compliance: str | None = None
    impact: str = Field(default="medium")
    likelihood: str = Field(default="possible")
    include_fact: bool = Field(default=True)


class ChatRequest(BaseModel):
    message: str
    system_prompt: str | None = None


@app.on_event("startup")
def _ensure_data_dir():
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(_HTML_PAGE)


@app.post("/api/brief")
async def api_brief(payload: BriefRequest):
    response = build_security_brief(
        prompt=payload.prompt,
        audience=payload.audience,
        topic=payload.topic,
        compliance_standard=payload.compliance,
        impact=payload.impact,
        likelihood=payload.likelihood,
        include_fact=payload.include_fact,
    )
    return {
        "message": response.message,
        "fact": response.fact,
        "tool_calls": [call.name for call in response.tool_calls],
    }


@app.post("/api/chat")
async def api_chat(payload: ChatRequest):
    try:
        result = llm_interface.generate(payload.message, system_prompt=payload.system_prompt)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"response": result.response, "provider": result.provider}


_HTML_PAGE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Iron Dillo Control Room</title>
  <style>
    :root { font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif; background:#0d1117; color:#f0f6fc; }
    body { margin:0; padding:0; }
    .shell { max-width:1200px; margin:0 auto; padding:2rem 1rem 3rem; }
    h1 { font-size:2.25rem; margin-bottom:0.5rem; }
    h2 { margin-top:0; }
    p { color:#8b949e; }
    .grid { display:grid; gap:1.5rem; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
    .card { background:#161b22; border:1px solid #30363d; border-radius:16px; padding:1.5rem; box-shadow:0 10px 40px rgba(0,0,0,0.45); }
    label { display:block; font-weight:600; margin-top:0.75rem; }
    input, select, textarea { width:100%; background:#0d1117; color:#f0f6fc; border:1px solid #30363d; border-radius:8px; padding:0.65rem; margin-top:0.35rem; }
    textarea { min-height:120px; resize:vertical; }
    button { margin-top:1rem; padding:0.75rem 1.5rem; border-radius:999px; border:none; background:linear-gradient(120deg,#0ba5ec,#2563eb); color:#fff; font-weight:600; cursor:pointer; }
    button:disabled { opacity:0.6; cursor:wait; }
    pre { background:#0d1117; color:#f0f6fc; border:1px solid #30363d; border-radius:12px; padding:1rem; min-height:140px; white-space:pre-wrap; }
    .tag { display:inline-flex; gap:0.35rem; align-items:center; background:#1f6feb33; border-radius:999px; padding:0.2rem 0.9rem; font-size:0.85rem; margin-right:0.35rem; }
    footer { margin-top:2rem; text-align:center; color:#6e7681; }
  </style>
</head>
<body>
  <div class=\"shell\">
    <header>
      <h1>Iron Dillo Control Room</h1>
      <p>Enterprise-ready GUI blending structured briefings, compliance callouts, and a modern chat interface.</p>
    </header>
    <div class=\"grid\">
      <section class=\"card\">
        <h2>Security Brief Generator</h2>
        <form id=\"brief-form\">
          <label>Prompt<input name=\"prompt\" required placeholder=\"How do I brief the board on ransomware?\" /></label>
          <label>Audience
            <select name=\"audience\">
              <option value=\"individuals\">Individuals</option>
              <option value=\"small_businesses\" selected>Small businesses</option>
              <option value=\"rural_operations\">Rural operations</option>
            </select>
          </label>
          <label>Topic
            <select name=\"topic\">
              <option value=\"identity\">Identity</option>
              <option value=\"devices\">Devices</option>
            </select>
          </label>
          <label>Compliance framework<input name=\"compliance\" placeholder=\"nist-csf\" /></label>
          <label>Impact<select name=\"impact\"><option>low</option><option selected>medium</option><option>high</option></select></label>
          <label>Likelihood<select name=\"likelihood\"><option>unlikely</option><option selected>possible</option><option>likely</option></select></label>
          <label><input type=\"checkbox\" name=\"include_fact\" checked /> Include rotating fact</label>
          <button type=\"submit\">Build brief</button>
        </form>
        <div id=\"brief-meta\"></div>
        <pre id=\"brief-output\">Run your first brief to see results.</pre>
      </section>
      <section class=\"card\">
        <h2>Modern LLM Chat</h2>
        <form id=\"chat-form\">
          <label>Message<textarea name=\"message\" required placeholder=\"Summarise the latest phishing trends for executives.\"></textarea></label>
          <label>System prompt<textarea name=\"system_prompt\" placeholder=\"Optional system instructions\"></textarea></label>
          <button type=\"submit\">Send</button>
        </form>
        <div class=\"tag\" id=\"chat-provider\">Provider: pending</div>
        <pre id=\"chat-output\">No conversation yet.</pre>
      </section>
    </div>
    <footer>Runs locally via FastAPI &amp; Uvicorn. Point a browser to the configured host/port to begin.</footer>
  </div>
  <script>
    const briefForm = document.getElementById('brief-form');
    const briefOutput = document.getElementById('brief-output');
    const briefMeta = document.getElementById('brief-meta');
    const chatForm = document.getElementById('chat-form');
    const chatOutput = document.getElementById('chat-output');
    const chatProvider = document.getElementById('chat-provider');

    briefForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      briefOutput.textContent = 'Building brief...';
      const formData = new FormData(briefForm);
      const payload = Object.fromEntries(formData.entries());
      payload.include_fact = formData.get('include_fact') === 'on';
      try {
        const response = await fetch('/api/brief', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail);
        }
        const data = await response.json();
        briefOutput.textContent = data.message + (data.fact ? '\n\nFun fact: ' + data.fact : '');
        briefMeta.textContent = 'Tools engaged: ' + data.tool_calls.join(', ');
      } catch (error) {
        briefOutput.textContent = 'Error generating brief: ' + error.message;
      }
    });

    chatForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      chatOutput.textContent = 'Contacting model...';
      const formData = new FormData(chatForm);
      const payload = Object.fromEntries(formData.entries());
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail);
        }
        const data = await response.json();
        chatProvider.textContent = 'Provider: ' + data.provider;
        chatOutput.textContent = data.response;
      } catch (error) {
        chatOutput.textContent = 'Chat failed: ' + error.message;
      }
    });
  </script>
</body>
</html>"""


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Launch the Iron Dillo GUI server")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development only)",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the default browser after starting",
    )
    args = parser.parse_args(argv)

    import uvicorn
    import webbrowser

    config = uvicorn.Config("iron_dillo.gui:app", host=args.host, port=args.port, reload=args.reload)
    server = uvicorn.Server(config)

    if args.open_browser:
        url = f"http://{args.host}:{args.port}"
        webbrowser.open(url)

    server.run()


if __name__ == "__main__":  # pragma: no cover
    main()

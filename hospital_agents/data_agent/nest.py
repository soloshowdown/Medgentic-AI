"""Tiny local stub for a minimal 'nest' agent API used by the project.

This implements:
- @tool decorator to mark callable tools
- Agent class to hold metadata and tools
- run(agent, port=...) which starts a tiny HTTP server exposing:
  - GET / -> agent info
  - POST /tool/<tool_name> -> invoke the tool with JSON body as kwargs

This is intentionally minimal and dependency-free so the repository can run
without installing an external "nest" package. It's suitable for local
testing and hackathon/demo purposes.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import functools
import threading
from urllib.parse import urlparse


def tool(func):
    """Decorator to mark a function as a nest tool."""
    func._is_nest_tool = True
    return func


class Agent:
    def __init__(self, name: str, instructions: str = "", tools=None):
        self.name = name
        self.instructions = instructions
        self.tools = {}
        if tools:
            for t in tools:
                # store by function name
                self.tools[getattr(t, "__name__", str(t))] = t


def _json_response(handler, obj, status=200):
    data = json.dumps(obj).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def run(agent: Agent, port: int = 8010):
    """Start a tiny HTTP server exposing agent tools.

    Endpoints:
    - GET /           -> {name, instructions, tools: [names]}
    - POST /tool/<t>  -> JSON body passed as kwargs to the tool; returns JSON result
    """

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                _json_response(self, {
                    "name": agent.name,
                    "instructions": agent.instructions,
                    "tools": list(agent.tools.keys()),
                })
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            parsed = urlparse(self.path)
            parts = parsed.path.strip("/").split("/")
            if len(parts) == 2 and parts[0] == "tool":
                tool_name = parts[1]
                func = agent.tools.get(tool_name)
                if func is None:
                    _json_response(self, {"error": f"Unknown tool '{tool_name}'"}, status=404)
                    return

                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b""
                try:
                    body = json.loads(raw.decode("utf-8")) if raw else {}
                except Exception:
                    _json_response(self, {"error": "Invalid JSON body"}, status=400)
                    return

                # allow body to be a dict of kwargs
                try:
                    if isinstance(body, dict):
                        result = func(**body)
                    else:
                        # if body isn't a dict, pass it as single arg
                        result = func(body)
                    _json_response(self, {"result": result})
                except Exception as e:
                    _json_response(self, {"error": str(e)}, status=500)
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # keep server quiet by default; print minimal info
            print("[nest stub] %s - - %s" % (self.address_string(), format % args))

    server = HTTPServer(("", port), Handler)

    print(f"[nest stub] Agent '{agent.name}' listening on port {port}. Tools: {list(agent.tools.keys())}")

    try:
        # Run server in current thread (blocking). If you want non-blocking, run in a thread.
        server.serve_forever()
    except KeyboardInterrupt:
        print("[nest stub] Shutting down")
        server.shutdown()

from __future__ import annotations

import contextlib
import functools
import http.server
import json
import socket
import subprocess
import threading
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"


class FrontendHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, {key: value or "" for key, value in attrs}))


@contextlib.contextmanager
def serve_frontend() -> Iterator[str]:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        _, port = sock.getsockname()

    handler = functools.partial(Handler, directory=str(FRONTEND_DIR))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def run_node_script(script: str) -> str:
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_frontend_files_exist() -> None:
    for path in [
        FRONTEND_DIR / "index.html",
        FRONTEND_DIR / "styles.css",
        FRONTEND_DIR / "app.js",
    ]:
        assert path.exists(), f"Missing frontend file: {path}"


def test_html_contains_expected_accessible_controls() -> None:
    parser = FrontendHtmlParser()
    parser.feed((FRONTEND_DIR / "index.html").read_text(encoding="utf-8"))

    tags = parser.tags
    assert any(tag == "form" for tag, _ in tags)
    assert any(tag == "textarea" and attrs.get("id") == "question-input" for tag, attrs in tags)
    assert any(tag == "label" and attrs.get("for") == "question-input" for tag, attrs in tags)
    assert any(tag == "button" and attrs.get("type") == "submit" for tag, attrs in tags)
    assert any(
        tag == "div"
        and attrs.get("id") == "response-message"
        and attrs.get("aria-live") == "polite"
        for tag, attrs in tags
    )
    assert any(
        tag == "div" and attrs.get("id") == "error-message" and attrs.get("role") == "alert"
        for tag, attrs in tags
    )


def test_javascript_has_valid_syntax() -> None:
    subprocess.run(
        ["node", "--check", str(FRONTEND_DIR / "app.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_empty_questions_are_rejected() -> None:
    output = run_node_script(
        """
        const frontend = await import("./frontend/app.js");
        const result = frontend.validateQuestion("   ");
        process.stdout.write(JSON.stringify(result));
        """,
    )
    parsed = json.loads(output)
    assert parsed["isValid"] is False
    assert "Escribe una pregunta" in parsed["message"]


def test_valid_questions_produce_a_simulated_answer() -> None:
    output = run_node_script(
        """
        const frontend = await import("./frontend/app.js");
        const result = await frontend.simulateAiRequest("Como funciona Lambda?", {
          delayMs: 1,
          search: "",
        });
        process.stdout.write(result);
        """,
    )
    assert 'Esta es una respuesta simulada para la pregunta: "Como funciona Lambda?".' in output
    assert "AWS Lambda y Amazon Bedrock" in output


def test_success_flow_resets_loading_and_renders_safe_text() -> None:
    output = run_node_script(
        """
        const frontend = await import("./frontend/app.js");

        function createFakeElement(initial = {}) {
          return {
            value: "",
            textContent: "",
            hidden: true,
            disabled: false,
            attributes: {},
            listeners: {},
            focusCalled: false,
            addEventListener(type, handler) {
              this.listeners[type] = handler;
            },
            setAttribute(name, value) {
              this.attributes[name] = String(value);
            },
            getAttribute(name) {
              return this.attributes[name] ?? null;
            },
            focus() {
              this.focusCalled = true;
            },
            ...initial,
          };
        }

        const elements = {
          form: createFakeElement(),
          questionInput: createFakeElement({ value: "<strong>hola</strong>" }),
          submitButton: createFakeElement(),
          loadingIndicator: createFakeElement({ hidden: true }),
          responseMessage: createFakeElement({ hidden: true }),
          errorMessage: createFakeElement({ hidden: true }),
          questionCounter: createFakeElement(),
        };

        let loadingSnapshot = null;
        const requestFn = async (question) => {
          loadingSnapshot = {
            disabled: elements.submitButton.disabled,
            loadingHidden: elements.loadingIndicator.hidden,
            busy: elements.form.getAttribute("aria-busy"),
            requestQuestion: question,
          };
          return frontend.buildSimulatedAnswer(question);
        };

        const app = frontend.createApp(elements, { requestFn, locationSearch: "" });
        await app.handleSubmit({ preventDefault() {} });

        process.stdout.write(JSON.stringify({
          loadingSnapshot,
          responseText: elements.responseMessage.textContent,
          responseHidden: elements.responseMessage.hidden,
          errorHidden: elements.errorMessage.hidden,
          errorText: elements.errorMessage.textContent,
          disabledAfter: elements.submitButton.disabled,
          loadingHiddenAfter: elements.loadingIndicator.hidden,
          busyAfter: elements.form.getAttribute("aria-busy"),
        }));
        """,
    )
    parsed = json.loads(output)
    assert parsed["loadingSnapshot"]["disabled"] is True
    assert parsed["loadingSnapshot"]["loadingHidden"] is False
    assert parsed["loadingSnapshot"]["busy"] == "true"
    assert parsed["loadingSnapshot"]["requestQuestion"] == "<strong>hola</strong>"
    assert "<strong>hola</strong>" in parsed["responseText"]
    assert parsed["responseHidden"] is False
    assert parsed["errorHidden"] is True
    assert parsed["errorText"] == ""
    assert parsed["disabledAfter"] is False
    assert parsed["loadingHiddenAfter"] is True
    assert parsed["busyAfter"] == "false"


def test_error_flow_resets_loading_and_preserves_input() -> None:
    output = run_node_script(
        """
        const frontend = await import("./frontend/app.js");

        function createFakeElement(initial = {}) {
          return {
            value: "",
            textContent: "",
            hidden: true,
            disabled: false,
            attributes: {},
            listeners: {},
            focusCalled: false,
            addEventListener(type, handler) {
              this.listeners[type] = handler;
            },
            setAttribute(name, value) {
              this.attributes[name] = String(value);
            },
            getAttribute(name) {
              return this.attributes[name] ?? null;
            },
            focus() {
              this.focusCalled = true;
            },
            ...initial,
          };
        }

        const elements = {
          form: createFakeElement(),
          questionInput: createFakeElement({ value: "Provocar error" }),
          submitButton: createFakeElement(),
          loadingIndicator: createFakeElement({ hidden: true }),
          responseMessage: createFakeElement({ hidden: true }),
          errorMessage: createFakeElement({ hidden: true }),
          questionCounter: createFakeElement(),
        };

        const requestFn = async () => {
          const message =
            "No se pudo generar la respuesta simulada. " +
            "Prueba de nuevo en unos segundos.";
          throw new Error(message);
        };

        const app = frontend.createApp(elements, { requestFn, locationSearch: "" });
        await app.handleSubmit({ preventDefault() {} });

        process.stdout.write(JSON.stringify({
          errorText: elements.errorMessage.textContent,
          errorHidden: elements.errorMessage.hidden,
          responseHidden: elements.responseMessage.hidden,
          disabledAfter: elements.submitButton.disabled,
          loadingHiddenAfter: elements.loadingIndicator.hidden,
          busyAfter: elements.form.getAttribute("aria-busy"),
          preservedQuestion: elements.questionInput.value,
        }));
        """,
    )
    parsed = json.loads(output)
    assert "No se pudo generar la respuesta simulada" in parsed["errorText"]
    assert parsed["errorHidden"] is False
    assert parsed["responseHidden"] is True
    assert parsed["disabledAfter"] is False
    assert parsed["loadingHiddenAfter"] is True
    assert parsed["busyAfter"] == "false"
    assert parsed["preservedQuestion"] == "Provocar error"


def test_repeated_submissions_are_blocked_while_request_is_running() -> None:
    output = run_node_script(
        """
        const frontend = await import("./frontend/app.js");

        function createFakeElement(initial = {}) {
          return {
            value: "",
            textContent: "",
            hidden: true,
            disabled: false,
            attributes: {},
            listeners: {},
            addEventListener(type, handler) {
              this.listeners[type] = handler;
            },
            setAttribute(name, value) {
              this.attributes[name] = String(value);
            },
            getAttribute(name) {
              return this.attributes[name] ?? null;
            },
            focus() {},
            ...initial,
          };
        }

        const elements = {
          form: createFakeElement(),
          questionInput: createFakeElement({ value: "Una sola vez" }),
          submitButton: createFakeElement(),
          loadingIndicator: createFakeElement({ hidden: true }),
          responseMessage: createFakeElement({ hidden: true }),
          errorMessage: createFakeElement({ hidden: true }),
          questionCounter: createFakeElement(),
        };

        let callCount = 0;
        let releaseRequest;
        const pendingRequest = new Promise((resolve) => {
          releaseRequest = resolve;
        });

        const requestFn = async () => {
          callCount += 1;
          return pendingRequest;
        };

        const app = frontend.createApp(elements, { requestFn, locationSearch: "" });
        const firstSubmit = app.handleSubmit({ preventDefault() {} });
        const secondSubmit = app.handleSubmit({ preventDefault() {} });
        releaseRequest("Respuesta final");
        await Promise.all([firstSubmit, secondSubmit]);

        process.stdout.write(JSON.stringify({
          callCount,
          responseText: elements.responseMessage.textContent,
          disabledAfter: elements.submitButton.disabled,
        }));
        """,
    )
    parsed = json.loads(output)
    assert parsed["callCount"] == 1
    assert parsed["responseText"] == "Respuesta final"
    assert parsed["disabledAfter"] is False

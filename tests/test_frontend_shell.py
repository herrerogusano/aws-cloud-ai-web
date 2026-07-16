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

NODE_FRONTEND_HELPERS = """
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

function createElements(questionValue = "") {
  return {
    form: createFakeElement(),
    questionInput: createFakeElement({ value: questionValue }),
    submitButton: createFakeElement(),
    loadingIndicator: createFakeElement({ hidden: true }),
    responseMessage: createFakeElement({ hidden: true }),
    errorMessage: createFakeElement({ hidden: true }),
    questionCounter: createFakeElement(),
  };
}

function createFakeHeaders(values = {}) {
  return {
    get(name) {
      const requestedName = String(name).toLowerCase();
      for (const [key, value] of Object.entries(values)) {
        if (key.toLowerCase() === requestedName) {
          return value;
        }
      }
      return null;
    },
  };
}

function createJsonResponse({
  ok = true,
  status = 200,
  headers = { "Content-Type": "application/json" },
  body = {},
} = {}) {
  return {
    ok,
    status,
    headers: createFakeHeaders(headers),
    async json() {
      return body;
    },
  };
}
"""


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
        FRONTEND_DIR / "config.js",
        FRONTEND_DIR / "config.example.js",
    ]:
        assert path.exists(), f"Missing frontend file: {path}"


def test_html_contains_expected_accessible_controls_and_scripts() -> None:
    parser = FrontendHtmlParser()
    parser.feed((FRONTEND_DIR / "index.html").read_text(encoding="utf-8"))

    tags = parser.tags
    assert any(tag == "form" for tag, _ in tags)
    assert any(
        tag == "textarea"
        and attrs.get("id") == "question-input"
        and attrs.get("placeholder") == "Escribe aqui tu pregunta..."
        for tag, attrs in tags
    )
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
    assert any(
        tag == "script" and attrs.get("src") == "./config.js" and "type" not in attrs
        for tag, attrs in tags
    )
    assert any(
        tag == "script" and attrs.get("src") == "./app.js" and attrs.get("type") == "module"
        for tag, attrs in tags
    )


def test_javascript_has_valid_syntax() -> None:
    for path in [
        FRONTEND_DIR / "app.js",
        FRONTEND_DIR / "config.js",
        FRONTEND_DIR / "config.example.js",
    ]:
        subprocess.run(
            ["node", "--check", str(path)],
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


def test_missing_configuration_is_reported_and_submit_stays_disabled() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("Hola");
        const app = frontend.createApp(elements, {{ appConfig: {{ apiUrl: "" }} }});

        process.stdout.write(JSON.stringify({{
          errorText: elements.errorMessage.textContent,
          errorHidden: elements.errorMessage.hidden,
          submitDisabled: elements.submitButton.disabled,
          configurationErrorMessage: app.getState().configurationErrorMessage,
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["errorText"] == "La aplicacion no esta disponible en este momento."
    assert parsed["errorHidden"] is False
    assert parsed["submitDisabled"] is True
    assert parsed["configurationErrorMessage"] == parsed["errorText"]


def test_request_creation_uses_post_json_trimmed_question_and_configured_url() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("  Que es AWS Lambda?  ");
        let requestSnapshot = null;

        const requestFn = async (question, options) => {{
          const result = await frontend.requestAnswer(question, {{
            apiUrl: options.apiUrl,
            fetchImpl: async (url, init) => {{
              requestSnapshot = {{
                url,
                method: init.method,
                contentType: init.headers["Content-Type"],
                body: init.body,
                hasSignal: Boolean(init.signal),
              }};
              return createJsonResponse({{
                body: {{
                  answer: "<strong>Respuesta segura</strong>",
                }},
              }});
            }},
          }});

          return result;
        }};

        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        await app.handleSubmit({{ preventDefault() {{}} }});

        process.stdout.write(JSON.stringify({{
          requestSnapshot,
          responseText: elements.responseMessage.textContent,
          disabledAfter: elements.submitButton.disabled,
          busyAfter: elements.form.getAttribute("aria-busy"),
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["requestSnapshot"]["url"] == "https://example.com/function-url"
    assert parsed["requestSnapshot"]["method"] == "POST"
    assert parsed["requestSnapshot"]["contentType"] == "application/json"
    assert json.loads(parsed["requestSnapshot"]["body"]) == {"question": "Que es AWS Lambda?"}
    assert parsed["requestSnapshot"]["hasSignal"] is True
    assert parsed["responseText"] == "<strong>Respuesta segura</strong>"
    assert parsed["disabledAfter"] is False
    assert parsed["busyAfter"] == "false"


def test_success_flow_resets_loading_and_renders_safe_text() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("<strong>hola</strong>");
        let loadingSnapshot = null;

        const requestFn = async (question, options) => {{
          const result = await frontend.requestAnswer(question, {{
            apiUrl: options.apiUrl,
            fetchImpl: async () => {{
              loadingSnapshot = {{
                disabled: elements.submitButton.disabled,
                loadingHidden: elements.loadingIndicator.hidden,
                busy: elements.form.getAttribute("aria-busy"),
                requestQuestion: question,
              }};

              return createJsonResponse({{
                body: {{
                  answer: [
                    "Respuesta generada para",
                    "<strong>texto seguro</strong>.",
                  ].join(" "),
                }},
              }});
            }},
          }});

          return result;
        }};

        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        await app.handleSubmit({{ preventDefault() {{}} }});

        process.stdout.write(JSON.stringify({{
          loadingSnapshot,
          responseText: elements.responseMessage.textContent,
          responseHidden: elements.responseMessage.hidden,
          errorHidden: elements.errorMessage.hidden,
          disabledAfter: elements.submitButton.disabled,
          loadingHiddenAfter: elements.loadingIndicator.hidden,
          busyAfter: elements.form.getAttribute("aria-busy"),
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["loadingSnapshot"]["disabled"] is True
    assert parsed["loadingSnapshot"]["loadingHidden"] is False
    assert parsed["loadingSnapshot"]["busy"] == "true"
    assert parsed["loadingSnapshot"]["requestQuestion"] == "<strong>hola</strong>"
    assert "<strong>texto seguro</strong>" in parsed["responseText"]
    assert parsed["responseHidden"] is False
    assert parsed["errorHidden"] is True
    assert parsed["disabledAfter"] is False
    assert parsed["loadingHiddenAfter"] is True
    assert parsed["busyAfter"] == "false"


def test_frontend_public_copy_does_not_contain_obsolete_phase_language() -> None:
    html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8").lower()

    forbidden_phrases = [
        "respuesta simulada",
        "respuesta fija",
        "bedrock permanece fuera de alcance",
        "antes de conectar amazon bedrock",
        "esta fase sigue ejecutandose en local",
        "frontend local",
        "lambda function url",
        "aws",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in html


def test_frontend_sync_script_excludes_non_public_files() -> None:
    script = (REPO_ROOT / "scripts" / "sync_frontend.ps1").read_text(encoding="utf-8")

    assert "config.example.js" in script
    assert "--delete" in script
    assert "frontend/" in script


def test_backend_validation_error_is_displayed_and_input_is_preserved() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("   ");
        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
        }});

        elements.questionInput.value = "Provocar validacion";

        const requestFn = async (question, options) =>
          frontend.requestAnswer(question, {{
            apiUrl: options.apiUrl,
            fetchImpl: async () =>
              createJsonResponse({{
                ok: false,
                status: 400,
                body: {{
                  error: {{
                    code: "INVALID_REQUEST",
                    message: "La pregunta es obligatoria.",
                  }},
                }},
              }}),
          }});

        const failingApp = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        await failingApp.handleSubmit({{ preventDefault() {{}} }});

        process.stdout.write(JSON.stringify({{
          errorText: elements.errorMessage.textContent,
          errorHidden: elements.errorMessage.hidden,
          responseHidden: elements.responseMessage.hidden,
          disabledAfter: elements.submitButton.disabled,
          loadingHiddenAfter: elements.loadingIndicator.hidden,
          busyAfter: elements.form.getAttribute("aria-busy"),
          preservedQuestion: elements.questionInput.value,
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["errorText"] == "La pregunta es obligatoria."
    assert parsed["errorHidden"] is False
    assert parsed["responseHidden"] is True
    assert parsed["disabledAfter"] is False
    assert parsed["loadingHiddenAfter"] is True
    assert parsed["busyAfter"] == "false"
    assert parsed["preservedQuestion"] == "Provocar validacion"


def test_malformed_success_response_is_reported_as_controlled_error() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("Pregunta valida");

        const requestFn = async (question, options) =>
          frontend.requestAnswer(question, {{
            apiUrl: options.apiUrl,
            fetchImpl: async () =>
              createJsonResponse({{
                body: {{
                  wrongField: "sin answer",
                }},
              }}),
          }});

        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        await app.handleSubmit({{ preventDefault() {{}} }});

        process.stdout.write(JSON.stringify({{
          errorText: elements.errorMessage.textContent,
          responseHidden: elements.responseMessage.hidden,
          disabledAfter: elements.submitButton.disabled,
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["errorText"] == "No se ha podido obtener una respuesta. Intentalo de nuevo."
    assert parsed["responseHidden"] is True
    assert parsed["disabledAfter"] is False


def test_network_error_shows_connection_message_and_restores_loading_state() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("Conexion");

        const requestFn = async (question, options) =>
          frontend.requestAnswer(question, {{
            apiUrl: options.apiUrl,
            fetchImpl: async () => {{
              throw new TypeError("Failed to fetch");
            }},
          }});

        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        await app.handleSubmit({{ preventDefault() {{}} }});

        process.stdout.write(JSON.stringify({{
          errorText: elements.errorMessage.textContent,
          errorHidden: elements.errorMessage.hidden,
          disabledAfter: elements.submitButton.disabled,
          loadingHiddenAfter: elements.loadingIndicator.hidden,
          busyAfter: elements.form.getAttribute("aria-busy"),
        }}));
        """,
    )
    parsed = json.loads(output)
    assert (
        parsed["errorText"]
        == "No se ha podido conectar con el servicio. Comprueba tu conexion e intentalo de nuevo."
    )
    assert parsed["errorHidden"] is False
    assert parsed["disabledAfter"] is False
    assert parsed["loadingHiddenAfter"] is True
    assert parsed["busyAfter"] == "false"


def test_timeout_aborts_request_and_reports_specific_message() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("Timeout");
        let abortObserved = false;

        const requestFn = async (question, options) =>
          frontend.requestAnswer(question, {{
            apiUrl: options.apiUrl,
            timeoutMs: 5,
            fetchImpl: async (url, init) =>
              new Promise((resolve, reject) => {{
                init.signal.addEventListener("abort", () => {{
                  abortObserved = init.signal.aborted;
                  const error = new Error("Aborted");
                  error.name = "AbortError";
                  reject(error);
                }});
              }}),
          }});

        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        await app.handleSubmit({{ preventDefault() {{}} }});

        process.stdout.write(JSON.stringify({{
          abortObserved,
          errorText: elements.errorMessage.textContent,
          disabledAfter: elements.submitButton.disabled,
          loadingHiddenAfter: elements.loadingIndicator.hidden,
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["abortObserved"] is True
    assert parsed["errorText"] == (
        "La solicitud esta tardando demasiado. Intentalo de nuevo en unos segundos."
    )
    assert parsed["disabledAfter"] is False
    assert parsed["loadingHiddenAfter"] is True


def test_repeated_submissions_are_blocked_while_request_is_running() -> None:
    output = run_node_script(
        f"""
        const frontend = await import("./frontend/app.js");
        {NODE_FRONTEND_HELPERS}

        const elements = createElements("Una sola vez");
        let callCount = 0;
        let releaseRequest;
        const pendingRequest = new Promise((resolve) => {{
          releaseRequest = resolve;
        }});

        const requestFn = async () => {{
          callCount += 1;
          return pendingRequest;
        }};

        const app = frontend.createApp(elements, {{
          appConfig: {{ apiUrl: "https://example.com/function-url" }},
          requestFn,
        }});

        const firstSubmit = app.handleSubmit({{ preventDefault() {{}} }});
        const secondSubmit = app.handleSubmit({{ preventDefault() {{}} }});
        releaseRequest("Respuesta final");
        await Promise.all([firstSubmit, secondSubmit]);

        process.stdout.write(JSON.stringify({{
          callCount,
          responseText: elements.responseMessage.textContent,
          disabledAfter: elements.submitButton.disabled,
        }}));
        """,
    )
    parsed = json.loads(output)
    assert parsed["callCount"] == 1
    assert parsed["responseText"] == "Respuesta final"
    assert parsed["disabledAfter"] is False

export const MAX_QUESTION_LENGTH = 1000;
export const REQUEST_TIMEOUT_MS = 25000;
export const GENERIC_REQUEST_ERROR_MESSAGE =
    "No se ha podido obtener una respuesta. Intentalo de nuevo.";
export const NETWORK_ERROR_MESSAGE =
    "No se ha podido conectar con el servicio. Comprueba tu conexion e intentalo de nuevo.";
export const TIMEOUT_ERROR_MESSAGE =
    "La solicitud esta tardando demasiado. Intentalo de nuevo en unos segundos.";
export const CONFIGURATION_ERROR_MESSAGE =
    "La aplicacion no esta disponible en este momento.";

class PublicError extends Error {}

export function normalizeQuestion(value) {
    return typeof value === "string" ? value.trim() : "";
}

export function validateQuestion(value, maxLength = MAX_QUESTION_LENGTH) {
    const normalizedQuestion = normalizeQuestion(value);

    if (!normalizedQuestion) {
        return {
            isValid: false,
            message: "Escribe una pregunta antes de enviarla.",
        };
    }

    if (normalizedQuestion.length > maxLength) {
        return {
            isValid: false,
            message: `La pregunta no puede superar los ${maxLength} caracteres.`,
        };
    }

    return {
        isValid: true,
        normalizedQuestion,
    };
}

export function isHttpUrl(value) {
    if (typeof value !== "string") {
        return false;
    }

    try {
        const parsedUrl = new URL(value);
        return parsedUrl.protocol === "http:" || parsedUrl.protocol === "https:";
    } catch {
        return false;
    }
}

export function getApiUrl(config = globalThis.APP_CONFIG) {
    const apiUrl = typeof config?.apiUrl === "string" ? config.apiUrl.trim() : "";

    if (!isHttpUrl(apiUrl)) {
        throw new PublicError(CONFIGURATION_ERROR_MESSAGE);
    }

    return apiUrl;
}

function readHeader(headers, name) {
    if (!headers) {
        return "";
    }

    if (typeof headers.get === "function") {
        return headers.get(name) ?? headers.get(name.toLowerCase()) ?? "";
    }

    if (headers instanceof Map) {
        for (const [key, value] of headers.entries()) {
            if (String(key).toLowerCase() === name.toLowerCase()) {
                return String(value);
            }
        }
    }

    if (typeof headers === "object") {
        for (const [key, value] of Object.entries(headers)) {
            if (key.toLowerCase() === name.toLowerCase()) {
                return String(value);
            }
        }
    }

    return "";
}

async function parseJsonBody(response) {
    const contentType = readHeader(response?.headers, "Content-Type").toLowerCase();

    if (!contentType.includes("application/json")) {
        throw new PublicError(GENERIC_REQUEST_ERROR_MESSAGE);
    }

    try {
        return await response.json();
    } catch {
        throw new PublicError(GENERIC_REQUEST_ERROR_MESSAGE);
    }
}

export async function parseApiResponse(response) {
    const payload = await parseJsonBody(response);

    if (response.ok) {
        if (typeof payload?.answer !== "string") {
            throw new PublicError(GENERIC_REQUEST_ERROR_MESSAGE);
        }

        return payload.answer;
    }

    const backendMessage =
        payload?.error && typeof payload.error === "object" ? payload.error.message : null;

    if (typeof backendMessage === "string" && backendMessage.trim()) {
        throw new PublicError(backendMessage.trim());
    }

    throw new PublicError(GENERIC_REQUEST_ERROR_MESSAGE);
}

export async function requestAnswer(question, options = {}) {
    const apiUrl = options.apiUrl ?? getApiUrl(options.config ?? globalThis.APP_CONFIG);
    const fetchImpl = options.fetchImpl ?? globalThis.fetch;
    const timeoutMs = options.timeoutMs ?? REQUEST_TIMEOUT_MS;
    const abortController = options.abortController ?? new AbortController();

    if (typeof fetchImpl !== "function") {
        throw new PublicError(NETWORK_ERROR_MESSAGE);
    }

    const timeoutId = globalThis.setTimeout(() => {
        abortController.abort();
    }, timeoutMs);

    try {
        const response = await fetchImpl(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
            signal: abortController.signal,
        });

        return await parseApiResponse(response);
    } catch (error) {
        if (error instanceof PublicError) {
            throw error;
        }

        if (error instanceof Error && error.name === "AbortError") {
            throw new PublicError(TIMEOUT_ERROR_MESSAGE);
        }

        throw new PublicError(NETWORK_ERROR_MESSAGE);
    } finally {
        globalThis.clearTimeout(timeoutId);
    }
}

export function createApp(elements, options = {}) {
    const maxQuestionLength = options.maxQuestionLength ?? MAX_QUESTION_LENGTH;
    const requestFn = options.requestFn ?? requestAnswer;
    let isSubmitting = false;
    let apiUrl = "";
    let configurationErrorMessage = "";

    try {
        apiUrl = options.apiUrl ?? getApiUrl(options.appConfig ?? globalThis.APP_CONFIG);
    } catch (error) {
        configurationErrorMessage =
            error instanceof Error ? error.message : CONFIGURATION_ERROR_MESSAGE;
    }

    function updateCounter() {
        const length = elements.questionInput.value.length;
        elements.questionCounter.textContent = `${length} / ${maxQuestionLength}`;
    }

    function clearFeedback() {
        elements.responseMessage.hidden = true;
        elements.responseMessage.textContent = "";
        elements.errorMessage.hidden = true;
        elements.errorMessage.textContent = "";
    }

    function setLoadingState(isLoading) {
        isSubmitting = isLoading;
        elements.form.setAttribute("aria-busy", String(isLoading));
        elements.submitButton.disabled = isLoading;
        elements.submitButton.textContent = isLoading ? "Generando..." : "Preguntar";
        elements.loadingIndicator.hidden = !isLoading;
    }

    function showResponse(message) {
        elements.responseMessage.textContent = message;
        elements.responseMessage.hidden = false;
        elements.errorMessage.hidden = true;
        elements.errorMessage.textContent = "";
    }

    function showError(message) {
        elements.errorMessage.textContent = message;
        elements.errorMessage.hidden = false;
        elements.responseMessage.hidden = true;
        elements.responseMessage.textContent = "";
    }

    function applyConfigurationState() {
        if (!configurationErrorMessage) {
            elements.submitButton.disabled = false;
            return;
        }

        showError(configurationErrorMessage);
        elements.submitButton.disabled = true;
    }

    async function handleSubmit(event) {
        event.preventDefault();

        if (isSubmitting) {
            return;
        }

        if (configurationErrorMessage) {
            showError(configurationErrorMessage);
            return;
        }

        clearFeedback();
        const validationResult = validateQuestion(elements.questionInput.value, maxQuestionLength);

        if (!validationResult.isValid) {
            showError(validationResult.message);
            elements.questionInput.focus();
            return;
        }

        setLoadingState(true);

        try {
            const response = await requestFn(validationResult.normalizedQuestion, { apiUrl });
            showResponse(response);
        } catch (error) {
            const message =
                error instanceof Error && error.message
                    ? error.message
                    : GENERIC_REQUEST_ERROR_MESSAGE;
            showError(message);
        } finally {
            setLoadingState(false);

            if (configurationErrorMessage) {
                elements.submitButton.disabled = true;
            }
        }
    }

    elements.form.addEventListener("submit", handleSubmit);
    elements.questionInput.addEventListener("input", updateCounter);
    updateCounter();
    clearFeedback();
    applyConfigurationState();

    return {
        updateCounter,
        clearFeedback,
        setLoadingState,
        showResponse,
        showError,
        handleSubmit,
        getState() {
            return { isSubmitting, apiUrl, configurationErrorMessage };
        },
    };
}

function initializeFrontend() {
    const form = document.querySelector("#question-form");
    const questionInput = document.querySelector("#question-input");
    const submitButton = document.querySelector("#submit-button");
    const loadingIndicator = document.querySelector("#loading-indicator");
    const responseMessage = document.querySelector("#response-message");
    const errorMessage = document.querySelector("#error-message");
    const questionCounter = document.querySelector("#question-counter");

    if (
        !form ||
        !questionInput ||
        !submitButton ||
        !loadingIndicator ||
        !responseMessage ||
        !errorMessage ||
        !questionCounter
    ) {
        return null;
    }

    return createApp({
        form,
        questionInput,
        submitButton,
        loadingIndicator,
        responseMessage,
        errorMessage,
        questionCounter,
    });
}

if (typeof document !== "undefined") {
    initializeFrontend();
}

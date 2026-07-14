export const MAX_QUESTION_LENGTH = 1000;
export const SIMULATED_DELAY_MS = 1200;
export const ERROR_FLAG = "simulateError";

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

export function shouldSimulateError(search = "") {
    const params = new URLSearchParams(search);
    return params.get(ERROR_FLAG) === "1";
}

export function buildSimulatedAnswer(question) {
    return [
        `Esta es una respuesta simulada para la pregunta: "${question}".`,
        "La conexion con AWS Lambda y Amazon Bedrock se anadira en una fase posterior.",
    ].join("\n");
}

export function simulateAiRequest(question, options = {}) {
    const delayMs = options.delayMs ?? SIMULATED_DELAY_MS;
    const search = options.search ?? "";

    return new Promise((resolve, reject) => {
        globalThis.setTimeout(() => {
            if (shouldSimulateError(search)) {
                reject(
                    new Error(
                        "No se pudo generar la respuesta simulada. Prueba de nuevo en unos segundos.",
                    ),
                );
                return;
            }

            resolve(buildSimulatedAnswer(question));
        }, delayMs);
    });
}

export function createApp(elements, options = {}) {
    const maxQuestionLength = options.maxQuestionLength ?? MAX_QUESTION_LENGTH;
    const locationSearch = options.locationSearch ?? window.location.search;
    const requestFn = options.requestFn ?? simulateAiRequest;
    let isSubmitting = false;

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
        elements.submitButton.textContent = isLoading ? "Generando respuesta..." : "Enviar pregunta";
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

    async function handleSubmit(event) {
        event.preventDefault();

        if (isSubmitting) {
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
            const response = await requestFn(validationResult.normalizedQuestion, {
                search: locationSearch,
            });
            showResponse(response);
        } catch (error) {
            const message =
                error instanceof Error
                    ? error.message
                    : "Ha ocurrido un error inesperado al generar la respuesta simulada.";
            showError(message);
        } finally {
            setLoadingState(false);
        }
    }

    elements.form.addEventListener("submit", handleSubmit);
    elements.questionInput.addEventListener("input", updateCounter);
    updateCounter();
    clearFeedback();

    return {
        updateCounter,
        clearFeedback,
        setLoadingState,
        showResponse,
        showError,
        handleSubmit,
        getState() {
            return { isSubmitting };
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

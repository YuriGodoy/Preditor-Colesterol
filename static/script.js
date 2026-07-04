const form = document.querySelector("#prediction-form");
const button = document.querySelector("#submit-button");
const resultPanel = document.querySelector(".result-panel");
const resultValue = document.querySelector("#result-value");
const resultMessage = document.querySelector("#result-message");

function buildPayload(formData) {
  return {
    grupo_sanguineo: formData.get("grupo_sanguineo"),
    fumante: formData.get("fumante"),
    nivel_atividade_fisica: formData.get("nivel_atividade_fisica"),
    idade: Number(formData.get("idade")),
    peso: Number(formData.get("peso")),
    altura: Number(formData.get("altura")),
  };
}

function setResult(value, message, state = "") {
  resultPanel.classList.remove("is-error", "is-warning");
  if (state) {
    resultPanel.classList.add(state);
  }
  resultValue.textContent = value;
  resultMessage.textContent = message;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  button.disabled = true;
  button.textContent = "Calculando...";
  setResult("--", "Enviando dados para a API.");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(buildPayload(new FormData(form))),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Não foi possível gerar a predição.");
    }

    const cholesterol = Number(data.colesterol);
    const state = cholesterol >= 240 ? "is-warning" : "";
    setResult(
      cholesterol.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }),
      "Estimativa retornada pelo modelo com base nas informações preenchidas.",
      state,
    );
  } catch (error) {
    setResult("Erro", error.message, "is-error");
  } finally {
    button.disabled = false;
    button.textContent = "Calcular colesterol";
  }
});

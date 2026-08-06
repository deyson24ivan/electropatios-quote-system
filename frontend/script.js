const form = document.querySelector("#quote-form");
const resultCard = document.querySelector("#result-card");

// La pagina envia el formulario a esta API local.
// Cuando el proyecto este online, esta URL se cambiara por el dominio real.
const API_URL = "http://localhost:5000/api/quotes";

// Estos nombres ayudan a mostrar una respuesta mas clara al cliente.
const categoryLabels = {
  lamparas: "lamparas",
  conectores: "conectores",
  cable: "cable",
  tuberia: "tuberia",
  proteccion: "breakers, tableros o tomas",
  herramientas: "herramientas y accesorios",
  otros: "otro producto",
};

// Convierte los campos del formulario en un objeto JSON para mandarlo a la API.
function formToPayload(formElement) {
  const data = new FormData(formElement);

  return {
    full_name: data.get("full_name"),
    email: data.get("email"),
    phone: data.get("phone"),
    customer_type: data.get("customer_type"),
    company_name: data.get("company_name"),
    request_type: data.get("request_type"),
    product_category: data.get("product_category"),
    quantity: data.get("quantity"),
    unit: data.get("unit"),
    budget: data.get("budget"),
    urgency: data.get("urgency"),
    delivery_city: data.get("delivery_city"),
    notes: data.get("notes"),
    source: "electropatios_web",
    consent: data.get("consent") === "on",
  };
}

// Muestra un mensaje bonito cuando la solicitud fue recibida.
function renderSuccess(response) {
  const quote = response.quote || {};
  const category = categoryLabels[quote.product_category] || "producto electrico";
  const title = response.duplicate
    ? "Ya recibimos una solicitud parecida"
    : "Solicitud enviada";

  resultCard.innerHTML = `
    <h2>${title}</h2>
    <p>
      Recibimos tu solicitud de ${quote.quantity || "-"} ${quote.unit || ""}
      de ${category}. Un asesor de Electropatios revisara disponibilidad,
      precio y entrega para contactarte.
    </p>
    <dl>
      <dt>Nombre</dt>
      <dd>${quote.full_name || "-"}</dd>
      <dt>Contacto</dt>
      <dd>${quote.phone || "-"}</dd>
      <dt>Ciudad o barrio</dt>
      <dd>${quote.delivery_city || "Por confirmar"}</dd>
    </dl>
  `;
}

// Muestra errores en lenguaje sencillo si falta algun dato.
function renderError(message, details = []) {
  resultCard.innerHTML = `
    <h2>Revisa la solicitud</h2>
    <p class="muted">${message}</p>
    ${
      details.length
        ? `<ul>${details.map((item) => `<li>${item}</li>`).join("")}</ul>`
        : ""
    }
  `;
}

// Esta parte escucha el boton del formulario y hace el envio.
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Enviando...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formToPayload(form)),
    });

    const body = await response.json();
    if (!response.ok) {
      renderError("Falta informacion para preparar la cotizacion.", body.messages || body.errors || []);
      return;
    }

    renderSuccess(body);
    form.reset();
  } catch (error) {
    renderError("No pudimos enviar la solicitud en este momento.", [error.message]);
  } finally {
    button.disabled = false;
    button.textContent = "Solicitar cotizacion";
  }
});

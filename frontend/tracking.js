const TRACKING_API_URL = "http://127.0.0.1:5000/api/tracking/events";
const TRACKING_SESSION_KEY = "electropatios_tracking_session";
const TRACKING_QUEUE_KEY = "electropatios_tracking_queue";
const UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"];

// Este archivo mide acciones importantes de la pagina.
// En local manda eventos a Flask; online los guarda como demo en el navegador.
const IS_LOCAL_TRACKING =
  window.location.protocol === "file:" ||
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

// Esta funcion crea un id sencillo para reconocer la visita actual.
function trackingId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `local-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

// La sesion queda guardada en el navegador para unir eventos de la misma visita.
function getTrackingSessionId() {
  let sessionId = localStorage.getItem(TRACKING_SESSION_KEY);
  if (!sessionId) {
    sessionId = trackingId();
    localStorage.setItem(TRACKING_SESSION_KEY, sessionId);
  }
  return sessionId;
}

// Lee los parametros UTM del link con el que llego el cliente.
function getUtmParams() {
  const params = new URLSearchParams(window.location.search);
  return UTM_KEYS.reduce((utm, key) => {
    utm[key] = params.get(key) || "";
    return utm;
  }, {});
}

// Si no hay UTM, dejo una fuente local para no guardar eventos vacios.
function getAttribution() {
  const utm = getUtmParams();
  return {
    ...utm,
    source: utm.utm_source || (IS_LOCAL_TRACKING ? "direct_local" : "direct_online"),
    medium: utm.utm_medium || (IS_LOCAL_TRACKING ? "local" : "portfolio"),
    campaign: utm.utm_campaign || "sin_campana",
  };
}

function readTrackingQueue() {
  try {
    const queue = JSON.parse(localStorage.getItem(TRACKING_QUEUE_KEY) || "[]");
    return Array.isArray(queue) ? queue : [];
  } catch (error) {
    return [];
  }
}

function saveTrackingQueue(queue) {
  localStorage.setItem(TRACKING_QUEUE_KEY, JSON.stringify(queue.slice(-50)));
}

// Arma el evento con datos comunes de pagina, sesion y campana.
function buildEvent(eventName, metadata = {}) {
  const attribution = getAttribution();
  return {
    event_name: eventName,
    session_id: getTrackingSessionId(),
    page_path: `${window.location.pathname}${window.location.search}${window.location.hash}`,
    page_title: document.title,
    utm_source: attribution.utm_source,
    utm_medium: attribution.utm_medium,
    utm_campaign: attribution.utm_campaign,
    utm_term: attribution.utm_term,
    utm_content: attribution.utm_content,
    referrer: document.referrer,
    user_agent: navigator.userAgent,
    metadata: {
      ...metadata,
      source: attribution.source,
      medium: attribution.medium,
      campaign: attribution.campaign,
    },
  };
}

// Envia el evento a la API. Si falla, lo deja en cola local.
async function sendTrackingEvent(event) {
  if (!IS_LOCAL_TRACKING) {
    const queue = readTrackingQueue();
    queue.push({ ...event, mode: "online_demo" });
    saveTrackingQueue(queue);
    return;
  }

  try {
    const response = await fetch(TRACKING_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(event),
    });

    if (!response.ok) {
      throw new Error("tracking_api_error");
    }
  } catch (error) {
    const queue = readTrackingQueue();
    queue.push(event);
    saveTrackingQueue(queue);
  }
}

// Intenta mandar eventos que quedaron pendientes si antes la API estaba apagada.
async function flushTrackingQueue() {
  if (!IS_LOCAL_TRACKING) return;

  const queue = readTrackingQueue();
  if (!queue.length) return;

  saveTrackingQueue([]);
  for (const event of queue) {
    await sendTrackingEvent(event);
  }
}

// Funcion publica que usa la pagina para medir acciones importantes.
function trackEvent(eventName, metadata = {}) {
  const event = buildEvent(eventName, metadata);
  sendTrackingEvent(event);
  return event;
}

window.ElectropatiosTracking = {
  trackEvent,
  getAttribution,
  getTrackingSessionId,
  flushTrackingQueue,
};

flushTrackingQueue();
trackEvent("page_view", {
  viewport_width: window.innerWidth,
  viewport_height: window.innerHeight,
});

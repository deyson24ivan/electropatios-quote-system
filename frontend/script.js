const form = document.querySelector("#quote-form");
const productGrid = document.querySelector("#product-grid");
const categoryTabs = document.querySelector("#category-tabs");
const searchInput = document.querySelector("#search-input");
const cartCount = document.querySelector("#cart-count");
const cartItems = document.querySelector("#cart-items");
const drawerItems = document.querySelector("#drawer-items");
const cartDrawer = document.querySelector("#cart-drawer");
const cartToggle = document.querySelector("#cart-toggle");
const closeCart = document.querySelector("#close-cart");
const clearCartButton = document.querySelector("#clear-cart");
const resultCard = document.querySelector("#result-card");
const catalogCount = document.querySelector("#catalog-count");

// Aqui decido por donde se envia el pedido.
// En mi PC uso n8n/API. En GitHub Pages uso modo demo para que no falle por localhost.
const API_URL = "http://localhost:5000/api/quotes";
const N8N_WEBHOOK_URL = "http://127.0.0.1:5678/webhook/electropatios-order";
const DEMO_ORDERS_STORAGE_KEY = "electropatios_demo_orders";
const IS_LOCAL_DEVELOPMENT =
  window.location.protocol === "file:" ||
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";
const USE_N8N_WEBHOOK = IS_LOCAL_DEVELOPMENT;
const ORDER_URL = USE_N8N_WEBHOOK ? N8N_WEBHOOK_URL : API_URL;
const CART_STORAGE_KEY = "electropatios_cart";

function track(eventName, metadata = {}) {
  if (!window.ElectropatiosTracking) return;
  window.ElectropatiosTracking.trackEvent(eventName, metadata);
}

function trackingAttribution() {
  if (!window.ElectropatiosTracking) {
    return {
      source: IS_LOCAL_DEVELOPMENT ? "direct_local" : "direct_online",
      medium: IS_LOCAL_DEVELOPMENT ? "local" : "portfolio",
      campaign: "sin_campana",
    };
  }
  return window.ElectropatiosTracking.getAttribution();
}

// Catalogo local de la pagina. Despues puede salir de MySQL, Sheets o un inventario real.
const products = [
  {
    sku: "LAM-LED-18W",
    name: "Panel LED 18W redondo",
    category: "lamparas",
    unit: "unidad",
    detail: "Panel para cielo raso en espacios residenciales y locales comerciales.",
    highlights: ["Luz blanca o calida", "Marco blanco", "Instalacion empotrada"],
  },
  {
    sku: "LAM-REF-50W",
    name: "Reflector LED 50W",
    category: "lamparas",
    unit: "unidad",
    detail: "Reflector para fachadas, patios, bodegas y zonas exteriores.",
    highlights: ["Uso exterior", "Alta iluminacion", "Ideal para seguridad"],
  },
  {
    sku: "LAM-BOM-12W",
    name: "Bombillo LED 12W",
    category: "lamparas",
    unit: "unidad",
    detail: "Bombillo LED para reemplazo rapido en hogares y negocios.",
    highlights: ["Rosca estandar", "Bajo consumo", "Luz diaria"],
  },
  {
    sku: "CAB-THHN-12",
    name: "Cable THHN #12",
    category: "cable",
    unit: "metro",
    detail: "Cable de cobre para instalaciones electricas residenciales y comerciales.",
    highlights: ["Por metro", "Uso interno", "Calibre comun"],
  },
  {
    sku: "CAB-THHN-10",
    name: "Cable THHN #10",
    category: "cable",
    unit: "metro",
    detail: "Cable para circuitos que requieren mayor capacidad, segun revision tecnica.",
    highlights: ["Por metro", "Cobre", "Para circuitos dedicados"],
  },
  {
    sku: "CAB-DUP-2X12",
    name: "Cable duplex 2x12",
    category: "cable",
    unit: "metro",
    detail: "Cable flexible para conexiones, extensiones y trabajos de mantenimiento.",
    highlights: ["Flexible", "Venta por metro", "Uso residencial"],
  },
  {
    sku: "TUB-PVC-12",
    name: "Tuberia PVC 1/2 pulgada",
    category: "tuberia",
    unit: "tubo",
    detail: "Tuberia para canalizar cableado en muros, techos y puntos electricos.",
    highlights: ["PVC", "Canalizacion", "Accesorios compatibles"],
  },
  {
    sku: "TUB-PVC-34",
    name: "Tuberia PVC 3/4 pulgada",
    category: "tuberia",
    unit: "tubo",
    detail: "Tuberia para canalizaciones con mayor espacio de cableado.",
    highlights: ["PVC", "Mayor diametro", "Obra y mantenimiento"],
  },
  {
    sku: "TUB-EMT-34",
    name: "Tuberia EMT 3/4 pulgada",
    category: "tuberia",
    unit: "tubo",
    detail: "Tuberia metalica para instalaciones visibles o comerciales.",
    highlights: ["Metalica", "Instalacion visible", "Mayor resistencia"],
  },
  {
    sku: "CON-REG-12P",
    name: "Regleta de conexion 12 polos",
    category: "conectores",
    unit: "unidad",
    detail: "Conector para derivaciones y empalmes organizados.",
    highlights: ["12 polos", "Conexion ordenada", "Uso en cajas"],
  },
  {
    sku: "CON-TER-AZ",
    name: "Terminal azul tipo pala",
    category: "conectores",
    unit: "paquete",
    detail: "Terminal para conexiones limpias en tableros y equipos.",
    highlights: ["Paquete", "Conexion firme", "Trabajo tecnico"],
  },
  {
    sku: "CON-CAJA-2X4",
    name: "Caja 2x4 para toma",
    category: "conectores",
    unit: "unidad",
    detail: "Caja para instalar tomacorrientes, interruptores o tapas.",
    highlights: ["Formato 2x4", "Para muro", "Uso comun"],
  },
  {
    sku: "PRO-BRK-20A",
    name: "Breaker 20A",
    category: "proteccion",
    unit: "unidad",
    detail: "Proteccion para circuitos residenciales, segun revision del caso.",
    highlights: ["20 amperios", "Proteccion", "Requiere seleccion tecnica"],
  },
  {
    sku: "PRO-TOMA-DOBLE",
    name: "Tomacorriente doble",
    category: "proteccion",
    unit: "unidad",
    detail: "Toma doble para hogares, locales y oficinas.",
    highlights: ["Doble salida", "Color blanco", "Uso interior"],
  },
  {
    sku: "PRO-TABL-8C",
    name: "Tablero 8 circuitos",
    category: "proteccion",
    unit: "unidad",
    detail: "Tablero para distribuir y proteger circuitos electricos.",
    highlights: ["8 circuitos", "Distribucion", "Para proyectos"],
  },
  {
    sku: "HER-CINTA",
    name: "Cinta aislante",
    category: "herramientas",
    unit: "unidad",
    detail: "Consumible basico para terminaciones y trabajos electricos.",
    highlights: ["Negra", "Uso general", "Alta rotacion"],
  },
  {
    sku: "HER-MULT",
    name: "Multimetro digital",
    category: "herramientas",
    unit: "unidad",
    detail: "Herramienta para medicion y revision de circuitos.",
    highlights: ["Digital", "Medicion basica", "Para tecnicos"],
  },
  {
    sku: "HER-GUIA-15M",
    name: "Guia pasacable 15 m",
    category: "herramientas",
    unit: "unidad",
    detail: "Guia para pasar cable en tuberia y canalizaciones.",
    highlights: ["15 metros", "Flexible", "Instalacion"],
  },
];

const categoryLabels = {
  todos: "Todos",
  lamparas: "Lamparas",
  cable: "Cable",
  tuberia: "Tuberia",
  conectores: "Conectores",
  proteccion: "Breakers y tomas",
  herramientas: "Herramientas",
};

let selectedCategory = "todos";
let cart = readCart();

// Recupera el carrito si el cliente recarga la pagina.
function readCart() {
  try {
    const storedCart = JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || "[]");
    return Array.isArray(storedCart) ? storedCart : [];
  } catch (error) {
    return [];
  }
}

// Guarda el carrito en el navegador para no perder el pedido al recargar.
function saveCart() {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
}

// Dibuja los botones de categorias del catalogo.
function renderCategoryTabs() {
  categoryTabs.innerHTML = Object.entries(categoryLabels)
    .map(
      ([category, label]) => `
        <button class="${category === selectedCategory ? "active" : ""}" data-category="${category}" type="button">
          ${label}
        </button>
      `
    )
    .join("");
}

// Decide que productos se muestran con categoria y busqueda.
function visibleProducts() {
  const search = searchInput.value.trim().toLowerCase();
  return products.filter((product) => {
    const matchesCategory = selectedCategory === "todos" || product.category === selectedCategory;
    const matchesSearch = [product.name, product.sku, product.detail, product.category, ...product.highlights]
      .join(" ")
      .toLowerCase()
      .includes(search);
    return matchesCategory && matchesSearch;
  });
}

// Muestra los productos como tarjetas con datos comerciales claros.
function renderProducts() {
  const filteredProducts = visibleProducts();
  catalogCount.textContent = `${filteredProducts.length} producto${filteredProducts.length === 1 ? "" : "s"} disponible${
    filteredProducts.length === 1 ? "" : "s"
  }`;

  productGrid.innerHTML = filteredProducts
    .map(
      (product) => `
        <article class="product-card">
          <div class="product-visual visual-${product.category}" aria-hidden="true"></div>
          <div class="product-body">
            <div class="product-meta">
              <span class="sku">${product.sku}</span>
              <span class="category-pill">${categoryLabels[product.category]}</span>
            </div>
            <h3>${product.name}</h3>
            <p>${product.detail}</p>
            <ul class="product-list">
              ${product.highlights.map((highlight) => `<li>${highlight}</li>`).join("")}
            </ul>
          </div>
          <div class="product-footer">
            <span>Venta por ${product.unit}</span>
            <button type="button" data-add="${product.sku}">Agregar</button>
          </div>
        </article>
      `
    )
    .join("");

  if (!filteredProducts.length) {
    productGrid.innerHTML = `<p class="muted">No encontre productos con esa busqueda. Puedes escribir la referencia en el detalle del pedido.</p>`;
  }
}

// Cambia la categoria y baja al catalogo.
function selectCategory(category) {
  selectedCategory = category;
  renderCategoryTabs();
  renderProducts();
  track("category_filter", {
    category,
    source: "category_strip",
  });
  document.querySelector("#productos").scrollIntoView({ behavior: "smooth", block: "start" });
}

// Agrega un producto al pedido o aumenta su cantidad si ya estaba.
function addToCart(sku) {
  const product = products.find((item) => item.sku === sku);
  if (!product) return;

  const existing = cart.find((item) => item.sku === sku);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ ...product, quantity: 1 });
  }

  saveCart();
  renderCart();
  cartDrawer.classList.add("open");
  track("product_add", {
    sku: product.sku,
    name: product.name,
    category: product.category,
    quantity: existing ? existing.quantity : 1,
    cart_items: cart.reduce((total, item) => total + item.quantity, 0),
  });
}

// Cambia cantidades dentro del pedido.
function updateCartQuantity(sku, change) {
  cart = cart
    .map((item) => {
      if (item.sku !== sku) return item;
      return { ...item, quantity: item.quantity + change };
    })
    .filter((item) => item.quantity > 0);

  saveCart();
  renderCart();
}

// Limpia todos los productos del pedido.
function clearCart(shouldTrack = true) {
  if (shouldTrack) {
    track("cart_clear", {
      cart_items: cart.reduce((total, item) => total + item.quantity, 0),
    });
  }
  cart = [];
  saveCart();
  renderCart();
}

// Dibuja el resumen del pedido en la pagina y en el panel lateral.
function renderCart() {
  const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
  cartCount.textContent = totalItems;

  const html = cart.length
    ? cart
        .map(
          (item) => `
            <div class="cart-row">
              <div>
                <strong>${item.name}</strong>
                <span>${item.sku} - ${item.unit}</span>
              </div>
              <div class="qty-controls" aria-label="Cantidad de ${item.name}">
                <button type="button" data-dec="${item.sku}" aria-label="Quitar uno">-</button>
                <span>${item.quantity}</span>
                <button type="button" data-inc="${item.sku}" aria-label="Agregar uno">+</button>
              </div>
            </div>
          `
        )
        .join("")
    : `<p class="muted">Agrega productos del catalogo para preparar tu pedido.</p>`;

  cartItems.innerHTML = html;
  drawerItems.innerHTML = html;
}

// Convierte el pedido completo en JSON para enviarlo a n8n o Python.
function formToPayload(formElement) {
  const data = new FormData(formElement);
  const mainItem = cart[0];
  const attribution = trackingAttribution();
  const itemSummary = cart
    .map((item) => `${item.quantity} ${item.unit} - ${item.name} (${item.sku})`)
    .join("; ");
  const notes = [
    itemSummary,
    data.get("notes"),
    data.get("preferred_contact") ? `Contacto preferido: ${data.get("preferred_contact")}` : "",
  ]
    .filter(Boolean)
    .join(" | ");

  return {
    full_name: data.get("full_name"),
    email: data.get("email"),
    phone: data.get("phone"),
    customer_type: data.get("customer_type"),
    company_name: data.get("company_name"),
    request_type: "quote",
    product_category: mainItem ? mainItem.category : "",
    quantity: cart.reduce((total, item) => total + item.quantity, 0),
    unit: "item",
    budget: data.get("budget"),
    urgency: data.get("urgency"),
    delivery_city: data.get("delivery_city"),
    notes,
    items: cart.map((item) => ({
      sku: item.sku,
      name: item.name,
      category: item.category,
      quantity: item.quantity,
      unit: item.unit,
    })),
    source: attribution.source,
    tracking: {
      session_id: window.ElectropatiosTracking ? window.ElectropatiosTracking.getTrackingSessionId() : "",
      source: attribution.source,
      medium: attribution.medium,
      campaign: attribution.campaign,
      utm_source: attribution.utm_source || "",
      utm_medium: attribution.utm_medium || "",
      utm_campaign: attribution.utm_campaign || "",
      utm_term: attribution.utm_term || "",
      utm_content: attribution.utm_content || "",
    },
    consent: data.get("consent") === "on",
  };
}

// Intenta leer JSON de la respuesta aunque algun servicio responda diferente.
async function parseResponse(response) {
  const text = await response.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch (error) {
    return { message: text };
  }
}

function localId(prefix) {
  if (window.crypto && window.crypto.randomUUID) {
    return `${prefix}_${window.crypto.randomUUID()}`;
  }
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

function readDemoOrders() {
  try {
    const orders = JSON.parse(localStorage.getItem(DEMO_ORDERS_STORAGE_KEY) || "[]");
    return Array.isArray(orders) ? orders : [];
  } catch (error) {
    return [];
  }
}

function saveDemoOrder(order) {
  const orders = readDemoOrders();
  orders.push(order);
  localStorage.setItem(DEMO_ORDERS_STORAGE_KEY, JSON.stringify(orders.slice(-25)));
}

// Esta prioridad demo se parece a la del backend para que la pagina online se sienta completa.
function demoPriority(payload) {
  const budget = Number(String(payload.budget || "").replace(/\D/g, "")) || 0;
  const urgent = ["hoy", "24h"].includes(payload.urgency);
  const businessCustomer = ["empresa", "ferreteria", "constructora", "tecnico_electricista"].includes(
    payload.customer_type
  );
  const highValue = budget >= 2000000 || payload.quantity >= 100;

  if (urgent || highValue || (businessCustomer && payload.quantity >= 10)) {
    return "high";
  }
  if (payload.quantity >= 10 || businessCustomer || budget >= 500000) {
    return "medium";
  }
  return "low";
}

// En GitHub Pages no hay servidor. Guardo una respuesta local para que la demo no quede rota.
function createDemoOrderResponse(payload) {
  const now = new Date().toISOString();
  const priority = demoPriority(payload);
  const quote = {
    id: localId("quote_demo"),
    full_name: payload.full_name,
    email: payload.email,
    phone: payload.phone,
    product_category: payload.product_category,
    quantity: payload.quantity,
    priority,
    status: "demo_prepared",
    items: payload.items,
    created_at: now,
  };
  const lead = {
    id: localId("lead_demo"),
    quote_id: quote.id,
    full_name: payload.full_name,
    priority,
    pipeline_stage: priority === "high" ? "contactar_hoy" : "revisar_y_cotizar",
    created_at: now,
  };

  const order = {
    demo_mode: true,
    quote,
    lead,
    payload,
  };
  saveDemoOrder(order);

  return {
    ok: true,
    demo_mode: true,
    duplicate: false,
    storage: "browser_local_demo",
    quote,
    lead,
  };
}

// Muestra confirmacion cuando el pedido fue recibido por la API o por n8n.
function renderSuccess(response) {
  const quote = response.quote || {};
  const lead = response.lead || {};
  let title = "Pedido enviado";
  if (response.demo_mode) {
    title = "Pedido preparado";
  } else if (response.duplicate) {
    title = "Ya recibimos un pedido parecido";
  }
  const priority = lead.priority || response.priority || quote.priority || "pendiente";
  const message = response.demo_mode
    ? "La solicitud quedo guardada en esta demo online. En la version local se envia al flujo de Electropatios para seguimiento."
    : "Un asesor de Electropatios revisara precio, disponibilidad y entrega para contactarte.";

  resultCard.innerHTML = `
    <h2>${title}</h2>
    <p>
      Recibimos tu solicitud con ${quote.quantity || cart.length} producto(s).
      Prioridad: ${priority}. ${message}
    </p>
  `;
  resultCard.classList.add("visible");
}

// Muestra errores en lenguaje sencillo si falta algun dato.
function renderError(message, details = []) {
  const errorList = Array.isArray(details) ? details : [details];
  resultCard.innerHTML = `
    <h2>Revisa el pedido</h2>
    <p>${message}</p>
    ${
      errorList.length
        ? `<ul>${errorList.map((item) => `<li>${item}</li>`).join("")}</ul>`
        : ""
    }
  `;
  resultCard.classList.add("visible");
}

categoryTabs.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-category]");
  if (!button) return;
  selectedCategory = button.dataset.category;
  renderCategoryTabs();
  renderProducts();
  track("category_filter", {
    category: selectedCategory,
    source: "catalog_sidebar",
  });
});

document.addEventListener("click", (event) => {
  const addButton = event.target.closest("button[data-add]");
  const inc = event.target.closest("button[data-inc]");
  const dec = event.target.closest("button[data-dec]");
  const jump = event.target.closest("button[data-jump-category]");

  if (addButton) addToCart(addButton.dataset.add);
  if (inc) updateCartQuantity(inc.dataset.inc, 1);
  if (dec) updateCartQuantity(dec.dataset.dec, -1);
  if (jump) selectCategory(jump.dataset.jumpCategory);
});

searchInput.addEventListener("input", () => {
  renderProducts();
  const search = searchInput.value.trim();
  if (search.length >= 3) {
    track("catalog_search", {
      search,
      results: visibleProducts().length,
    });
  }
});

cartToggle.addEventListener("click", () => {
  cartDrawer.classList.add("open");
  track("cart_open", {
    cart_items: cart.reduce((total, item) => total + item.quantity, 0),
  });
});

closeCart.addEventListener("click", () => {
  cartDrawer.classList.remove("open");
});

clearCartButton.addEventListener("click", clearCart);

// Esta parte escucha el formulario y envia el pedido al flujo comercial.
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!cart.length) {
    track("quote_submit_error", {
      reason: "empty_cart",
    });
    renderError("Agrega al menos un producto antes de enviar el pedido.");
    return;
  }

  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  button.textContent = "Enviando...";
  track("quote_submit_attempt", {
    cart_items: cart.reduce((total, item) => total + item.quantity, 0),
    categories: [...new Set(cart.map((item) => item.category))].join(","),
  });

  try {
    const payload = formToPayload(form);
    if (!IS_LOCAL_DEVELOPMENT) {
      const body = createDemoOrderResponse(payload);
      track("quote_submit_success", {
        quote_id: body.quote.id,
        lead_id: body.lead.id,
        priority: body.lead.priority,
        duplicate: false,
        source: payload.source,
        campaign: payload.tracking.campaign,
        mode: "online_demo",
      });
      renderSuccess(body);
      form.reset();
      clearCart(false);
      cartDrawer.classList.remove("open");
      return;
    }

    const response = await fetch(ORDER_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const body = await parseResponse(response);
    if (!response.ok) {
      track("quote_submit_error", {
        status: response.status,
        errors: body.messages || body.errors || body.missing_fields || [],
      });
      renderError("Falta informacion para preparar el pedido.", body.messages || body.errors || body.missing_fields || []);
      return;
    }

    track("quote_submit_success", {
      quote_id: body.quote_id || (body.quote && body.quote.id) || "",
      lead_id: body.lead_id || (body.lead && body.lead.id) || "",
      priority: body.priority || (body.lead && body.lead.priority) || "",
      duplicate: Boolean(body.duplicate),
      source: payload.source,
      campaign: payload.tracking.campaign,
    });
    renderSuccess(body);
    form.reset();
    clearCart(false);
    cartDrawer.classList.remove("open");
  } catch (error) {
    track("quote_submit_error", {
      reason: "network_error",
      message: error.message,
    });
    renderError("No pudimos enviar el pedido en este momento.", [error.message]);
  } finally {
    button.disabled = false;
    button.textContent = "Enviar cotizacion";
  }
});

renderCategoryTabs();
renderProducts();
renderCart();

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
const resultCard = document.querySelector("#result-card");

// Aqui decido por donde se envia el pedido.
// Ahora los pedidos pasan primero por n8n para practicar automatizaciones.
// Si n8n esta apagado, se puede volver a false para mandar directo a Python.
const USE_N8N_WEBHOOK = true;
const API_URL = "http://localhost:5000/api/quotes";
const N8N_WEBHOOK_URL = "http://127.0.0.1:5678/webhook/electropatios-order";
const ORDER_URL = USE_N8N_WEBHOOK ? N8N_WEBHOOK_URL : API_URL;

// Catalogo inicial escrito en JavaScript para practicar.
// Despues puede venir de MySQL, Google Sheets o un inventario real.
const products = [
  {
    sku: "LAM-LED-18W",
    name: "Panel LED 18W redondo",
    category: "lamparas",
    unit: "unidad",
    detail: "Para cielo raso, luz blanca o calida segun disponibilidad.",
  },
  {
    sku: "LAM-REF-50W",
    name: "Reflector LED 50W",
    category: "lamparas",
    unit: "unidad",
    detail: "Uso exterior, ideal para fachadas, patios y bodegas.",
  },
  {
    sku: "CAB-THHN-12",
    name: "Cable THHN #12",
    category: "cable",
    unit: "metro",
    detail: "Cable de cobre para instalaciones electricas residenciales.",
  },
  {
    sku: "CAB-DUP-2X12",
    name: "Cable duplex 2x12",
    category: "cable",
    unit: "metro",
    detail: "Cable flexible para conexiones y extensiones.",
  },
  {
    sku: "TUB-PVC-12",
    name: "Tuberia PVC 1/2 pulgada",
    category: "tuberia",
    unit: "unidad",
    detail: "Tuberia para canalizacion de cableado electrico.",
  },
  {
    sku: "TUB-EMT-34",
    name: "Tuberia EMT 3/4 pulgada",
    category: "tuberia",
    unit: "unidad",
    detail: "Tuberia metalica para instalaciones visibles o industriales.",
  },
  {
    sku: "CON-REG-12P",
    name: "Regleta de conexion 12 polos",
    category: "conectores",
    unit: "unidad",
    detail: "Conector para derivaciones y empalmes ordenados.",
  },
  {
    sku: "CON-CAJA-2X4",
    name: "Caja 2x4 para toma",
    category: "conectores",
    unit: "unidad",
    detail: "Caja para tomacorrientes e interruptores.",
  },
  {
    sku: "PRO-BRK-20A",
    name: "Breaker 20A",
    category: "proteccion",
    unit: "unidad",
    detail: "Proteccion para circuitos residenciales.",
  },
  {
    sku: "PRO-TOMA-DOBLE",
    name: "Tomacorriente doble",
    category: "proteccion",
    unit: "unidad",
    detail: "Toma doble para uso residencial o comercial.",
  },
  {
    sku: "HER-CINTA",
    name: "Cinta aislante",
    category: "herramientas",
    unit: "unidad",
    detail: "Accesorio basico para terminaciones electricas.",
  },
  {
    sku: "HER-MULT",
    name: "Multimetro digital",
    category: "herramientas",
    unit: "unidad",
    detail: "Herramienta para medicion y revision de circuitos.",
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
let cart = [];

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

// Muestra los productos segun categoria y busqueda.
function renderProducts() {
  const search = searchInput.value.trim().toLowerCase();
  const visibleProducts = products.filter((product) => {
    const matchesCategory = selectedCategory === "todos" || product.category === selectedCategory;
    const matchesSearch = [product.name, product.sku, product.detail, product.category]
      .join(" ")
      .toLowerCase()
      .includes(search);
    return matchesCategory && matchesSearch;
  });

  productGrid.innerHTML = visibleProducts
    .map(
      (product) => `
        <article class="product-card">
          <div>
            <span class="sku">${product.sku}</span>
            <h3>${product.name}</h3>
            <p>${product.detail}</p>
          </div>
          <div class="product-footer">
            <span>${categoryLabels[product.category]}</span>
            <button type="button" data-add="${product.sku}">Agregar</button>
          </div>
        </article>
      `
    )
    .join("");

  if (!visibleProducts.length) {
    productGrid.innerHTML = `<p class="muted">No encontre productos con esa busqueda.</p>`;
  }
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

  renderCart();
  cartDrawer.classList.add("open");
}

// Cambia cantidades dentro del pedido.
function updateCartQuantity(sku, change) {
  cart = cart
    .map((item) => {
      if (item.sku !== sku) return item;
      return { ...item, quantity: item.quantity + change };
    })
    .filter((item) => item.quantity > 0);

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
              <div class="qty-controls">
                <button type="button" data-dec="${item.sku}">-</button>
                <span>${item.quantity}</span>
                <button type="button" data-inc="${item.sku}">+</button>
              </div>
            </div>
          `
        )
        .join("")
    : `<p class="muted">Agrega productos del catalogo para preparar tu pedido.</p>`;

  cartItems.innerHTML = html;
  drawerItems.innerHTML = html;
}

// Convierte el pedido completo en JSON para enviarlo a Python.
function formToPayload(formElement) {
  const data = new FormData(formElement);
  const mainItem = cart[0];
  const notes = data.get("notes");
  const itemSummary = cart
    .map((item) => `${item.quantity} ${item.unit} - ${item.name} (${item.sku})`)
    .join("; ");

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
    budget: "",
    urgency: data.get("urgency"),
    delivery_city: data.get("delivery_city"),
    notes: [itemSummary, notes].filter(Boolean).join(" | "),
    items: cart.map((item) => ({
      sku: item.sku,
      name: item.name,
      category: item.category,
      quantity: item.quantity,
      unit: item.unit,
    })),
    source: "electropatios_storefront",
    consent: data.get("consent") === "on",
  };
}

// Muestra confirmacion cuando el pedido fue recibido por la API.
function renderSuccess(response) {
  const quote = response.quote || {};
  const title = response.duplicate
    ? "Ya recibimos un pedido parecido"
    : "Pedido enviado";

  resultCard.innerHTML = `
    <h2>${title}</h2>
    <p>
      Recibimos tu solicitud con ${quote.quantity || cart.length} producto(s).
      Un asesor de Electropatios revisara precio, disponibilidad y entrega
      para contactarte.
    </p>
  `;
  resultCard.classList.add("visible");
}

// Muestra errores en lenguaje sencillo si falta algun dato.
function renderError(message, details = []) {
  resultCard.innerHTML = `
    <h2>Revisa el pedido</h2>
    <p>${message}</p>
    ${
      details.length
        ? `<ul>${details.map((item) => `<li>${item}</li>`).join("")}</ul>`
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
});

productGrid.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-add]");
  if (!button) return;
  addToCart(button.dataset.add);
});

document.addEventListener("click", (event) => {
  const inc = event.target.closest("button[data-inc]");
  const dec = event.target.closest("button[data-dec]");

  if (inc) updateCartQuantity(inc.dataset.inc, 1);
  if (dec) updateCartQuantity(dec.dataset.dec, -1);
});

searchInput.addEventListener("input", renderProducts);

cartToggle.addEventListener("click", () => {
  cartDrawer.classList.add("open");
});

closeCart.addEventListener("click", () => {
  cartDrawer.classList.remove("open");
});

// Esta parte escucha el formulario y envia el pedido al backend.
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!cart.length) {
    renderError("Agrega al menos un producto antes de enviar el pedido.");
    return;
  }

  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Enviando...";

  try {
    const response = await fetch(ORDER_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formToPayload(form)),
    });

    const body = await response.json();
    if (!response.ok) {
      renderError("Falta informacion para preparar el pedido.", body.messages || body.errors || body.missing_fields || []);
      return;
    }

    renderSuccess(body);
    form.reset();
    cart = [];
    renderCart();
    cartDrawer.classList.remove("open");
  } catch (error) {
    renderError("No pudimos enviar el pedido en este momento.", [error.message]);
  } finally {
    button.disabled = false;
    button.textContent = "Enviar pedido";
  }
});

renderCategoryTabs();
renderProducts();
renderCart();

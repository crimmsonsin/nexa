const productGrid = document.querySelector("#product-grid");
const feedback = document.querySelector("#feedback-text");
const API_URL = "http://localhost:5050/api";

async function renderProducts(category = "Todos") {
  feedback.textContent = "API consultando · conectando con el recomendador";
  try {
    const response = await fetch(`${API_URL}/recommendations?category=${encodeURIComponent(category)}`);
    if (!response.ok) throw new Error("API unavailable");
    const { recommendations } = await response.json();
    productGrid.innerHTML = recommendations.map((product) => `
    <article class="product-card">
      <div class="product-image" aria-hidden="true">${product.symbol}</div>
      <div class="product-content">
        <span class="product-category">${product.category}</span>
        <h3>${product.name}</h3>
        <p>${product.description}</p>
        <button class="interest-button" data-product-id="${product.id}">Me interesa <span aria-hidden="true">→</span></button>
      </div>
    </article>
  `).join("");
    feedback.textContent = category === "Todos"
      ? "API respondió · recomendaciones ordenadas por afinidad"
      : `API respondió · ${recommendations.length} recomendación${recommendations.length === 1 ? "" : "es"} para ${category.toLowerCase()}`;
  } catch (error) {
    productGrid.innerHTML = `<p class="api-error">No se pudo conectar con la API. Inicia los dos servicios del backend.</p>`;
    feedback.textContent = "API desconectada · revisa los servicios Python";
  }
}

productGrid.addEventListener("click", async (event) => {
  const button = event.target.closest(".interest-button");
  if (!button) return;
  button.disabled = true;
  try {
    const response = await fetch(`${API_URL}/preferences`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "demo-user", product_id: Number(button.dataset.productId) }),
    });
    if (!response.ok) throw new Error("Preference failed");
    button.textContent = "Preferencia guardada";
    feedback.textContent = "API respondió · preferencia persistida en SQLite";
  } catch (error) {
    button.disabled = false;
    feedback.textContent = "API error · no se pudo guardar la preferencia";
  }
});

document.querySelectorAll(".filter-button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".filter-button").forEach((item) => item.classList.remove("is-selected"));
    button.classList.add("is-selected");
    renderProducts(button.dataset.category);
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));
renderProducts();

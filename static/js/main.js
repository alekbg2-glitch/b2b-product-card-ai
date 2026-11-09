let samplesData = {};

document.addEventListener("DOMContentLoaded", async () => {
  // Загрузка образцов товаров
  try {
    const res1 = await fetch("/card-ai/api/samples/product_1");
    if (res1.ok) samplesData["product_1"] = await res1.json();
    
    const res2 = await fetch("/card-ai/api/samples/product_2");
    if (res2.ok) samplesData["product_2"] = await res2.json();
  } catch (err) {
    console.error("Ошибка загрузки образцов:", err);
  }

  // Кнопка быстрой загрузки образца 1 (ОВЕН)
  document.getElementById("btn-load-sample1")?.addEventListener("click", () => {
    if (samplesData["product_1"]) {
      document.getElementById("json-input").value = JSON.stringify(samplesData["product_1"], null, 2);
    }
  });

  // Кнопка быстрой загрузки образца 2 (Манотомь)
  document.getElementById("btn-load-sample2")?.addEventListener("click", () => {
    if (samplesData["product_2"]) {
      document.getElementById("json-input").value = JSON.stringify(samplesData["product_2"], null, 2);
    }
  });

  // Обработка отправки формы
  const form = document.getElementById("generate-form");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const rawJson = document.getElementById("json-input").value.trim();
    const alertBox = document.getElementById("error-alert");
    alertBox.classList.add("d-none");
    
    let parsedInput;
    try {
      parsedInput = JSON.parse(rawJson);
    } catch (jsonErr) {
      alertBox.textContent = "Ошибка: Введён некорректный JSON! Проверьте синтаксис (запятые, кавычки).";
      alertBox.classList.remove("d-none");
      return;
    }

    const loader = document.getElementById("loading-overlay");
    const resultContainer = document.getElementById("result-container");
    loader.classList.remove("d-none");

    try {
      const resp = await fetch("/card-ai/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsedInput)
      });

      if (!resp.ok) {
        const errData = await resp.json();
        throw new Error(errData.detail || `Ошибка сервера (${resp.status})`);
      }

      const card = await resp.json();
      renderCardResult(card);
      resultContainer.classList.remove("d-none");
      resultContainer.scrollIntoView({ behavior: "smooth" });
    } catch (apiErr) {
      alertBox.textContent = `Ошибка генерации: ${apiErr.message}`;
      alertBox.classList.remove("d-none");
    } finally {
      loader.classList.add("d-none");
    }
  });

  // Кнопки копирования
  document.getElementById("btn-copy-md")?.addEventListener("click", () => {
    const text = document.getElementById("raw-markdown").textContent;
    navigator.clipboard.writeText(text).then(() => {
      showToast("Markdown скопирован в буфер обмена!");
    });
  });

  document.getElementById("btn-copy-json")?.addEventListener("click", () => {
    const text = document.getElementById("raw-json").textContent;
    navigator.clipboard.writeText(text).then(() => {
      showToast("JSON скопирован в буфер обмена!");
    });
  });
});

function renderCardResult(card) {
  // SEO Title
  const titleElem = document.getElementById("res-seo-title");
  const titleCount = document.getElementById("res-seo-title-count");
  titleElem.textContent = card.seo_title;
  titleCount.textContent = `${card.seo_title_length} / 70 символов`;
  titleCount.className = `char-counter ${card.seo_title_length <= 70 ? 'valid' : 'invalid'}`;

  // SEO Description
  const descElem = document.getElementById("res-seo-desc");
  const descCount = document.getElementById("res-seo-desc-count");
  descElem.textContent = card.seo_description;
  descCount.textContent = `${card.seo_description_length} / 800-1200 символов`;
  descCount.className = `char-counter ${(card.seo_description_length >= 750 && card.seo_description_length <= 1300) ? 'valid' : 'invalid'}`;

  // Queries
  const queriesList = document.getElementById("res-search-queries");
  queriesList.innerHTML = card.search_queries.map(q => `<span class="badge-tag"><i class="bi bi-search me-1"></i>${q}</span>`).join("");

  // Specs
  const specsTbody = document.getElementById("res-specs-tbody");
  specsTbody.innerHTML = Object.entries(card.structured_specs).map(([k, v]) => `
    <tr>
      <td class="fw-medium text-nowrap">${k}</td>
      <td>${v === "данных нет" ? '<span class="badge bg-secondary">данных нет</span>' : v}</td>
    </tr>
  `).join("");

  // Commercial
  document.getElementById("res-target-audience").textContent = card.commercial_block.target_audience;
  
  const tasksUl = document.getElementById("res-tasks-list");
  tasksUl.innerHTML = card.commercial_block.key_tasks_solved.map(t => `<li>${t}</li>`).join("");

  const advUl = document.getElementById("res-adv-list");
  advUl.innerHTML = card.commercial_block.competitive_advantages.map(a => `<li>${a}</li>`).join("");

  // Warnings
  const warnWrapper = document.getElementById("res-warnings-wrapper");
  const warnList = document.getElementById("res-warnings-list");
  if (card.missing_data_warnings && card.missing_data_warnings.length > 0) {
    warnWrapper.classList.remove("d-none");
    warnList.innerHTML = card.missing_data_warnings.map(w => `<li>${w}</li>`).join("");
  } else {
    warnWrapper.classList.add("d-none");
  }

  // Raw formats
  document.getElementById("raw-markdown").textContent = card.raw_markdown;
  document.getElementById("raw-json").textContent = JSON.stringify(card, null, 2);
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "position-fixed bottom-0 end-0 p-3";
  toast.style.zIndex = "9999";
  toast.innerHTML = `
    <div class="toast show align-items-center text-white bg-dark border-0 shadow" role="alert">
      <div class="d-flex">
        <div class="toast-body"><i class="bi bi-check-circle-fill text-success me-2"></i>${message}</div>
      </div>
    </div>
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}

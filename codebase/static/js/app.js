(async function main() {

  /* ── 1. Init ── */
  console.log("Comprehension Gap Detector started.");

  /* ── 2. DOM refs ── */
  const chatStream       = document.getElementById("chatStream");
  const composer         = document.getElementById("composer");
  const questionInput    = document.getElementById("questionInput");
  const sendButton       = document.getElementById("sendButton");
  const themeSelect      = document.getElementById("themeSelect");
  const providerSelect   = document.getElementById("providerSelect");
  const slideHtmlFrame   = document.getElementById("slideHtmlFrame");
  const selectionPill    = document.getElementById("selectionPill");
  const selectionPreview = document.getElementById("selectionPreview");
  const selectionDisplay = document.getElementById("selectionDisplay");
  const selectionDisplayText = document.getElementById("selectionDisplayText");
  const selectionClearBtn    = document.getElementById("selectionClearBtn");

  /* ── 3. System prompt ── */
  let FULL_SLIDE_TEXT = "";
  let SLIDE_CONTEXT = "";

  function updateContext(selectedText) {
    SLIDE_CONTEXT = selectedText || "";
  }

  /* ── 4. Selection capture — nhận postMessage từ iframe slide ── */
  function applySelection(text) {
    const trimmed = (text || "").trim();
    if (trimmed.length > 2) {
      updateContext(trimmed);

      const preview = trimmed.length > 45 ? trimmed.substring(0, 45) + "…" : trimmed;
      selectionPreview.textContent = preview;
      selectionPill.classList.add("active");

      selectionDisplayText.textContent = trimmed;
      selectionDisplay.classList.add("active");

      questionInput.placeholder = "Đoạn đã bôi đen ở trên. Gõ câu hỏi của bạn...";
      questionInput.focus();
    }
  }

  function clearSelection() {
    updateContext("");
    selectionDisplay.classList.remove("active");
    selectionDisplayText.textContent = "";
    selectionPill.classList.remove("active");
    selectionPreview.textContent = "";
    questionInput.placeholder = "Bôi đen đoạn slide bên trái rồi gõ câu hỏi...";
  }

  selectionClearBtn.addEventListener("click", clearSelection);

  // Lắng nghe postMessage từ iframe slide
  window.addEventListener("message", function (event) {
    // Chỉ nhận từ đúng iframe, bỏ qua mọi source khác
    try {
      if (event.source !== slideHtmlFrame.contentWindow) return;
    } catch (e) { return; }
    
    if (!event.data) return;
    
    if (event.data.type === "SLIDE_FULL_TEXT") {
      FULL_SLIDE_TEXT = event.data.text;
      // Không cần build system prompt ở frontend nữa
      console.log("✓ Đã nhận toàn bộ nội dung bài giảng từ slide HTML");
    } else if (event.data.type === "SLIDE_SELECTION") {
      applySelection(event.data.text);
    }
  });

  /* ── 5. Theme & Provider selectors ── */
  function initThemeSelector() {
    const savedTheme = localStorage.getItem("app-theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    if (themeSelect) {
      themeSelect.value = savedTheme;
      themeSelect.addEventListener("change", (e) => {
        const theme = e.target.value;
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("app-theme", theme);
      });
    }
  }

  function initProviderSelector() {
    // Chỉ để frontend hiển thị UI bình thường
  }

  /* ── 7. Chat utilities ── */
  function scrollToLatest() {
    chatStream.scrollTop = chatStream.scrollHeight;
  }

  function wireTutorActions(root = document) {
    root.querySelectorAll(".feedback").forEach(btn => {
      btn.addEventListener("click", () => {
        btn.closest(".feedback-row").querySelectorAll(".feedback").forEach(b => b.classList.remove("selected"));
        btn.classList.add("selected");
      });
    });
    root.querySelectorAll(".skip").forEach(btn => {
      btn.addEventListener("click", () => {
        const wrap = btn.closest(".tutor-response")?.querySelector(".check-wrap");
        if (wrap) { 
          wrap.classList.add("hidden"); 
          btn.textContent = "Đã bỏ qua"; 
          btn.disabled = true; 
          // Phạt rate limit: chặn hỏi trong 2 lượt kế tiếp vì học viên đã skip
          RECENTLY_SKIPPED_COUNT = 2;
        }
      });
    });
  }

  function addStudentMessage(text) {
    const el = document.createElement("div");
    el.className = "message student";
    el.innerHTML = `<div class="bubble">${text.replace(/</g,"&lt;")}</div>`;
    chatStream.appendChild(el);
  }

  function addLoadingMessage(providerName) {
    const el = document.createElement("div");
    el.className = "message tutor loading";
    el.innerHTML = `<div class="bubble"><span class="spinner" aria-hidden="true"></span>Đang hỏi ${providerName}...</div>`;
    chatStream.appendChild(el);
    return el;
  }

  function renderTutorResponse(json) {
    const el = document.createElement("div");
    el.className = "message tutor";
    el.innerHTML = `
      <div class="bubble tutor-response">
        <div class="section answer">
          <h3>Trả lời:</h3>
          <p>${json.answer}</p>
        </div>
        <div class="section-divider"></div>
        <div class="misconception-wrap${json.misconception_detected ? "" : " hidden"}">
          <div class="section misconception">
            <h3>Có thể bạn đang nhầm:</h3>
            <p>${json.misconception_evidence || ""}</p>
          </div>
          <div class="section-divider"></div>
        </div>
        <div class="check-wrap${json.check_question ? "" : " hidden"}">
          <div class="section check">
            <h3>Câu kiểm tra nhanh:</h3>
            <p>${json.check_question || ""}</p>
          </div>
        </div>
        <div class="feedback-row">
          <button class="feedback" type="button">Hữu ích</button>
          <button class="feedback" type="button">Quá khó</button>
          <button class="feedback" type="button">Không liên quan</button>
          ${json.check_question ? `<button class="skip" type="button">Bỏ qua &rarr;</button>` : ""}
        </div>
      </div>`;
    chatStream.appendChild(el);
    wireTutorActions(el);
  }

  function renderError(message) {
    const el = document.createElement("div");
    el.className = "message tutor";
    el.innerHTML = `<div class="bubble" style="border-color:rgba(239,68,68,0.4);color:#fca5a5">${message}</div>`;
    chatStream.appendChild(el);
  }

  /* ── 8. Submit handler ── */
  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Ngăn xuống dòng
      composer.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
    }
  });

  composer.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = questionInput.value.trim();
    if (!text) return;

    const providerValue = providerSelect.value;
    const providerName = providerSelect.options[providerSelect.selectedIndex].text;

    addStudentMessage(text);
    questionInput.value = "";
    questionInput.disabled = true;
    sendButton.disabled = true;
    providerSelect.disabled = true;
    const loading = addLoadingMessage(providerName);
    scrollToLatest();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider: providerValue,
          userText: text,
          selectedText: SLIDE_CONTEXT,
          fullSlideText: FULL_SLIDE_TEXT
        })
      });
      
      if (!res.ok) {
        const errBody = await res.text();
        throw new Error(`HTTP ${res.status} - ${errBody}`);
      }
      
      const raw = await res.text();
      console.log("[DEBUG] Raw response:", raw.substring(0, 300));
      // Parse JSON
      let json;
      try {
        const cleaned = raw.replace(/^```(?:json)?\s*/m, "").replace(/\s*```$/m, "").trim();
        json = JSON.parse(cleaned);
      } catch (parseErr) {
        const match = raw.match(/\{[\s\S]*\}/);
        if (match) {
          json = JSON.parse(match[0]);
        } else {
          json = { answer: raw, misconception_detected: false, misconception_confidence: "low", misconception_evidence: "", check_question: "" };
        }
      }
      // --- Xác thực Misconception & Rate Limit ---
      const detected = String(json.misconception_detected).toLowerCase() === "true" || json.misconception_detected === true;
      const confidence = String(json.misconception_confidence || "").trim().toLowerCase();
      
      if (!json.misconception_evidence || json.misconception_evidence.trim() === "") {
        json.misconception_confidence = "low";
      } else {
        json.misconception_confidence = confidence;
      }
      json.misconception_detected = detected;

      let shouldShowQuestion = (json.misconception_detected === true && json.misconception_confidence === "high");
      
      if (shouldShowQuestion) {
        if (LAST_TURN_HAD_QUESTION || RECENTLY_SKIPPED_COUNT > 0) {
          shouldShowQuestion = false;
          LAST_TURN_HAD_QUESTION = false;
          if (RECENTLY_SKIPPED_COUNT > 0) RECENTLY_SKIPPED_COUNT--;
        } else {
          LAST_TURN_HAD_QUESTION = true;
        }
      } else {
        LAST_TURN_HAD_QUESTION = false;
      }

      if (!shouldShowQuestion) {
        json.check_question = "";
      }

      loading.remove();
      renderTutorResponse(json);
    } catch (err) {
      console.error("[ERROR]", err);
      loading.remove();
      renderError(`Lỗi ${providerName}: ${err.message}`);
    }

    questionInput.disabled = false;
    sendButton.disabled = false;
    providerSelect.disabled = false;
    questionInput.focus();
    scrollToLatest();
  });

  let LAST_TURN_HAD_QUESTION = false;
  let RECENTLY_SKIPPED_COUNT = 0;

  /* ── 9. Init ── */
  initThemeSelector();
  initProviderSelector();
  wireTutorActions();

})();

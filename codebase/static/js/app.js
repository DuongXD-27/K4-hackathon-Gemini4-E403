(async function main() {

  /* ── 1. Init ── */
  console.log("Comprehension Gap Detector started.");

  /* ── 2. DOM refs ── */
  const chatStream       = document.getElementById("chatStream");
  const composer         = document.getElementById("composer");
  const questionInput    = document.getElementById("questionInput");
  const sendButton       = document.getElementById("sendButton");
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
  let SYSTEM_PROMPT = buildSystemPrompt("");

  function buildSystemPrompt(selectedText) {
    const fullContext = FULL_SLIDE_TEXT 
      ? `\n\nNội dung toàn bộ bài giảng (để bạn có bối cảnh chung):\n---\n${FULL_SLIDE_TEXT}\n---\n` 
      : "";
    const ctx = selectedText && selectedText.trim()
      ? `Đoạn slide học viên đang bôi đen:\n---\n${selectedText.trim()}\n---`
      : "(Học viên chưa bôi đen đoạn nào. Hãy gợi ý họ bôi đen nội dung muốn hỏi.)";
    return `Bạn là AI Tutor trong nền tảng học AI Thực Chiến. Học viên đang đọc slide HTML và vừa bôi đen một đoạn rồi hỏi bạn.${fullContext}
${ctx}
Với MỖI câu hỏi, bạn BẮT BUỘC trả lời theo đúng cấu trúc JSON sau, không thêm gì khác ngoài JSON:
{
  "answer": "Câu trả lời giải thích khái niệm, dựa vào đoạn bôi đen nếu có. Nếu không có căn cứ trong đoạn, ghi rõ 'thông tin này ngoài đoạn đang xem'.",
  "misconception_detected": true hoặc false,
  "misconception_confidence": "high" hoặc "medium" hoặc "low",
  "misconception_evidence": "Trích dẫn/giải thích lý do vì sao học viên có vẻ đang nhầm lẫn",
  "check_question": "Câu hỏi kiểm tra nhanh (chỉ hiển thị nếu detected=true và confidence=high)"
}
Quy tắc:
- misconception_detected = true CHỈ KHI câu hỏi ẩn chứa nhầm lẫn rõ ràng.
- Bắt buộc phải có misconception_evidence rõ ràng thì mới được đặt misconception_confidence = "high".
- Đừng lúc nào cũng hỏi ngược lại học viên. Hãy cẩn thận khi flag misconception.
- Nếu câu hỏi quá mơ hồ và không có đoạn bôi đen làm ngữ cảnh: answer = "Bạn đang thắc mắc về phần nào cụ thể? Hãy mô tả thêm hoặc bôi đen đoạn bạn chưa hiểu nhé.", misconception_detected = false.
- Nếu câu hỏi ngắn gọn nhưng có thể suy luận từ đoạn bôi đen (ví dụ: "giải thích đoạn này", "là sao?"), hãy cố gắng giải thích đoạn slide đó.
- Luôn dùng tiếng Việt, giọng thân thiện như mentor.

Ví dụ đánh giá độ tự tin (misconception_confidence):
Ví dụ 1 (misconception_confidence = "high"):
- HV: "Fine-tune xong thì model sẽ tự động thêm tài liệu mới vào lúc trả lời đúng không?"
- Đánh giá: Nhầm lẫn giữa Fine-tuning và RAG (RAG mới là nạp tài liệu lúc hỏi), có bằng chứng rõ trong câu hỏi.
→ misconception_detected: true, misconception_confidence: "high"

Ví dụ 2 (misconception_confidence = "high"):
- HV: "Agent chỉ là LLM thôi đúng không?"
- Đánh giá: Nhầm lẫn rõ ràng — Agent = LLM (Reasoning) + Tools + Memory + Action, không chỉ riêng LLM trần.
→ misconception_detected: true, misconception_confidence: "high", check_question: "Theo bạn, ngoài bộ não LLM, agent cần thêm những thành phần nào để có thể tự hoàn thành một mục tiêu?"

Ví dụ 3 (misconception_confidence = "low"):
- HV: "Temperature cao thì output đa dạng hơn đúng không?"
- Đánh giá: HV đang hiểu đúng, không có nhầm lẫn.
→ misconception_detected: false, misconception_confidence: "low", check_question: ""`;
  }

  /* ── 4. Selection capture — nhận postMessage từ iframe slide ── */
  function applySelection(text) {
    const trimmed = (text || "").trim();
    if (trimmed.length > 8) {
      SLIDE_CONTEXT = trimmed;
      SYSTEM_PROMPT = buildSystemPrompt(trimmed);

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
    SLIDE_CONTEXT = "";
    SYSTEM_PROMPT = buildSystemPrompt("");
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
      // Build lại prompt để ăn context mới
      SYSTEM_PROMPT = buildSystemPrompt(SLIDE_CONTEXT);
      console.log("✓ Đã nhận toàn bộ nội dung bài giảng từ slide HTML");
    } else if (event.data.type === "SLIDE_SELECTION") {
      applySelection(event.data.text);
    }
  });

  /* ── 5. Provider selector (dữ liệu nạp từ HTML tĩnh, key ở backend) ── */
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
          systemPrompt: SYSTEM_PROMPT
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
  initProviderSelector();
  wireTutorActions();

})();

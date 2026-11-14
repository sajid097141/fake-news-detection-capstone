/* VERITAS frontend. Talks only to the local Flask endpoint POST /api/predict. */
(() => {
  "use strict";

  const API_URL = "/api/analyze";
  const TIMEOUT_MS = 60000;
  const $ = (id) => document.getElementById(id);

  const form = $("analyze-form");
  const titleEl = $("title");
  const articleEl = $("article");
  const charNum = $("char-num");
  const wordNum = $("word-num");
  const btn = $("analyze-btn");
  const btnLabel = $("btn-label");
  const clearBtn = $("clear-btn");
  const errorBox = $("form-error");
  const resultsSection = $("results");
  const resultPanel = $("result-panel");
  const srStatus = $("sr-status");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Input helpers ---------- */

  
  function updateInputState() {
    const text = articleEl.value;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    charNum.textContent = text.length.toLocaleString();
    wordNum.textContent = words.toLocaleString();
    
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
  }

  function clearError() {
    errorBox.textContent = "";
    errorBox.hidden = true;
  }

  function setLoading(isLoading) {
    btn.disabled = isLoading;
    btn.classList.toggle("is-loading", isLoading);
    btn.setAttribute("aria-busy", String(isLoading));
    btnLabel.textContent = isLoading ? "Analyzing…" : "Analyze text";
  }

  /* ---------- Response handling ---------- */

  // The backend uses 0 = Fake and 1 = Real; accept numbers or label strings.
  function normalizeLabel(raw) {
    if (raw === 0 || raw === "0") return "Fake";
    if (raw === 1 || raw === "1") return "Real";
    const s = String(raw).trim().toLowerCase();
    if (s.includes("fake")) return "Fake";
    if (s.includes("real")) return "Real";
    return null;
  }

  const clamp = (n) => Math.min(100, Math.max(0, n));

  // Accepts fractions (0-1) or percentages (0-100) and returns percentages.
  function toPercentages(result, label) {
    const fake = Number(result.probabilities && result.probabilities.Fake);
    const real = Number(result.probabilities && result.probabilities.Real);
    const conf = Number(result.confidence);

    if (Number.isFinite(fake) && Number.isFinite(real)) {
      const k = fake + real <= 1.5 ? 100 : 1;
      const f = clamp(fake * k);
      const r = clamp(real * k);
      return { fake: f, real: r, confidence: Number.isFinite(conf) ? clamp(conf * k) : Math.max(f, r) };
    }
    if (Number.isFinite(conf)) {
      const c = clamp(conf <= 1 ? conf * 100 : conf);
      return label === "Fake"
        ? { fake: c, real: 100 - c, confidence: c }
        : { fake: 100 - c, real: c, confidence: c };
    }
    return null;
  }

  function pickMessage(data, status) {
    const candidate = data && (data.message || data.error || data.detail);
    if (typeof candidate === "string" && candidate.trim()) return candidate;
    if (candidate && typeof candidate === "object") return JSON.stringify(candidate);
    return `The server could not process the request (HTTP ${status}).`;
  }

  function setMeter(prefix, value) {
    const bar = $(`prob-${prefix}-bar`);
    bar.style.width = "0%";
    void bar.offsetWidth; // restart the width transition
    bar.style.width = `${value}%`;
    $(`prob-${prefix}-value`).textContent = `${value.toFixed(1)}%`;
    $(`prob-${prefix}`).setAttribute("aria-valuenow", value.toFixed(1));
  }


  function makeEvidenceLink(url, label) {
    if (typeof url !== "string" || !/^https?:\\/\\//i.test(url)) return null;
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = label;
    return link;
  }

  function renderEvidence(evidence) {
    const factList = $("fact-evidence-list");
    const newsList = $("news-evidence-list");
    factList.replaceChildren();
    newsList.replaceChildren();

    const facts = evidence && evidence.fact_checks;
    if (!facts || facts.status !== "success" || !facts.result) {
      const message = document.createElement("p");
      message.className = "evidence-empty";
      message.textContent = facts && facts.message ? facts.message : "Fact-check reviews are temporarily unavailable.";
      factList.append(message);
    } else {
      const claims = facts.result.claims || [];
      if (!claims.length) {
        const empty = document.createElement("p");
        empty.className = "evidence-empty";
        empty.textContent = "No sufficiently relevant fact-check reviews were found.";
        factList.append(empty);
      }
      claims.forEach((claim) => {
        const card = document.createElement("article");
        card.className = "evidence-card";

        const relevance = document.createElement("span");
        relevance.className = "evidence-tag";
        relevance.textContent = claim.relevance && claim.relevance.label === "direct_match" ? "Direct match" : "Related claim";
        card.append(relevance);

        const claimTitle = document.createElement("h3");
        claimTitle.textContent = claim.claim_text || "Claim text unavailable";
        card.append(claimTitle);

        (claim.reviews || []).forEach((review) => {
          const reviewLine = document.createElement("p");
          reviewLine.className = "evidence-meta";
          reviewLine.textContent = [
            review.publisher || "Unknown publisher",
            review.textual_rating || "Rating not provided",
            review.review_date ? "Reviewed: " + review.review_date.slice(0, 10) : ""
          ].filter(Boolean).join(" · ");
          card.append(reviewLine);

          const link = makeEvidenceLink(review.url, review.title || "Read fact-check");
          if (link) {
            const linkWrap = document.createElement("p");
            linkWrap.className = "evidence-link";
            linkWrap.append(link);
            card.append(linkWrap);
          }
        });
        factList.append(card);
      });

      const excluded = facts.result.excluded_claims || [];
      if (excluded.length) {
        const note = document.createElement("p");
        note.className = "evidence-empty";
        note.textContent = excluded.length + " unrelated result(s) excluded by the keyword relevance filter.";
        factList.append(note);
      }
    }

    const news = evidence && evidence.news_coverage;
    if (!news || news.status !== "success" || !news.result) {
      const message = document.createElement("p");
      message.className = "evidence-empty";
      message.textContent = news && news.message ? news.message : "News coverage is temporarily unavailable.";
      newsList.append(message);
    } else {
      const articles = news.result.articles || [];
      if (!articles.length) {
        const empty = document.createElement("p");
        empty.className = "evidence-empty";
        empty.textContent = "No matching news articles were found in the selected time range.";
        newsList.append(empty);
      }
      articles.forEach((article) => {
        const card = document.createElement("article");
        card.className = "evidence-card";
        const heading = document.createElement("h3");
        heading.textContent = article.title || "Untitled article";
        const link = makeEvidenceLink(article.url, "Open source article");
        if (link) heading.replaceChildren(link);
        card.append(heading);

        const meta = document.createElement("p");
        meta.className = "evidence-meta";
        meta.textContent = [article.domain || "Unknown source", article.published_at || ""].filter(Boolean).join(" · ");
        card.append(meta);
        newsList.append(card);
      });
    }
  }

  function renderResult(data, headlineOnly) {
    const result = data.result || {};
    renderEvidence(data.evidence);
    const label = normalizeLabel(result.label);
    const pct = label ? toPercentages(result, label) : null;
    if (!label || !pct) {
      throw new Error("The server returned a response in an unexpected format.");
    }

    resultPanel.dataset.verdict = label.toLowerCase();
    $("verdict-label").textContent = label;
    $("verdict-sub").textContent =
      label === "Fake"
        ? "The wording resembles articles labelled Fake in the training data."
        : "The wording resembles articles labelled Real in the training data.";
    $("confidence-value").textContent = `${pct.confidence.toFixed(1)}%`;

    $("result-experimental").hidden = !(headlineOnly || result.experimental || data.experimental);
    if (typeof data.disclaimer === "string" && data.disclaimer.trim()) {
      $("result-disclaimer").textContent = data.disclaimer;
    }

    resultsSection.hidden = false;
    // Replay the reveal animation on every new result.
    resultPanel.style.animation = "none";
    void resultPanel.offsetWidth;
    resultPanel.style.animation = "";

    setMeter("fake", pct.fake);
    setMeter("real", pct.real);

    srStatus.textContent =
      `Prediction: ${label}, ${pct.confidence.toFixed(1)} percent confidence. This is a machine-learning prediction, not a fact check.`;
    resultsSection.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
  }

  /* ---------- Submit ---------- */

  async function onSubmit(event) {
    event.preventDefault();
    clearError();

    
const title = titleEl.value.trim();
    const article = articleEl.value.trim();

    if (!title && !article) {
      showError("Please enter a headline and the full article before analyzing.");
      titleEl.focus(); return;
    }
    if (title.length > 1000) {
      showError("Headline cannot exceed 1,000 characters.");
      titleEl.focus(); return;
    }
    if (article.length > 50000) {
      showError("Article cannot exceed 50,000 characters.");
      articleEl.focus(); return;
    }
    if (!article) {
      showError("Headline-only analysis is disabled. Please paste the full article.");
      articleEl.focus(); return;
    }
    if (article.length < 100) {
      showError("Article is too short. Please provide at least 100 characters.");
      articleEl.focus(); return;
    }
    const words = article.toLowerCase().match(/\b[\w']+\b/g) || [];
    if (words.length < 20) {
      showError("Please provide a more detailed article with at least 20 words.");
      articleEl.focus(); return;
    }
    if (/(.)\1{7,}/.test(article)) {
      showError("Your article contains unusually repeated characters. Please check the text.");
      articleEl.focus(); return;
    }
    const lines = article.split(/\r?\n/).map(line => line.trim().toLowerCase()).filter(line => line.length >= 30);
    if (lines.some((line, index) => lines.indexOf(line) !== index)) {
      showError("Your article contains repeated lines. Please check the text.");
      articleEl.focus(); return;
    }
    const uniqueRatio = new Set(words).size / words.length;
    if (words.length >= 30 && uniqueRatio < 0.30) {
      showError("Your article contains highly repetitive wording. Please provide genuine article text.");
      articleEl.focus(); return;
    }
    const headlineOnly = false;

    setLoading(true);
const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ title, article }),
        signal: controller.signal,
      });

      let data = null;
      try {
        data = await response.json();
      } catch (_) {
        data = null; // non-JSON body (for example an HTML error page)
      }

      const failedStatus = data && typeof data.status === "string" && /^(error|fail)/i.test(data.status);
      if (!response.ok || failedStatus || !data) {
        throw new Error(pickMessage(data, response.status));
      }
      renderResult(data, headlineOnly);
    } catch (err) {
      resultsSection.hidden = true;
      if (err.name === "AbortError") {
        showError("The request took too long. Check that the Flask server is running and try again.");
      } else if (err instanceof TypeError) {
        showError("Could not reach the server. Make sure the Flask app is running, then try again.");
      } else {
        showError(err.message || "Something went wrong. Please try again.");
      }
    } finally {
      clearTimeout(timer);
      setLoading(false);
    }
  }

  function onClear() {
    titleEl.value = "";
    articleEl.value = "";
    clearError();
    resultsSection.hidden = true;
    srStatus.textContent = "";
    updateInputState();
    titleEl.focus();
  }

  titleEl.addEventListener("input", updateInputState);
  articleEl.addEventListener("input", updateInputState);
  form.addEventListener("submit", onSubmit);
  clearBtn.addEventListener("click", onClear);
  updateInputState();
})();

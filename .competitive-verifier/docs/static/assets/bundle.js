// suzlib-bundle.js
// - Injects "Bundle" button on competitive-verifier generated pages
// - Bundles code by following "Depends on" section links recursively
// - Shows full-viewport modal (independent from sidebar layout)
// - Copy button at top, wide area, line-wrapped code (no horizontal scroll by default)
// - Optional syntax highlight if highlight.js (hljs) is present

(() => {
  "use strict";

  // ---------- small utilities ----------
  const IMP = "important";
  const MAX_Z = "2147483647";

  function setImp(el, prop, value) {
    el.style.setProperty(prop, value, IMP);
  }

  function normText(s) {
    return (s || "").replace(/\s+/g, " ").trim();
  }

  function absUrl(href, base) {
    return new URL(href, base).toString();
  }

  function sameOrigin(url) {
    try {
      return new URL(url, location.href).origin === location.origin;
    } catch {
      return false;
    }
  }

  function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  // ---------- extracting from HTML docs ----------
  function parseHtml(html) {
    return new DOMParser().parseFromString(html, "text/html");
  }

  function findH2(doc, title) {
    const hs = Array.from(doc.querySelectorAll("h2"));
    return hs.find((h) => normText(h.textContent) === title) || null;
  }

  function collectLinksUntilNextH2(h2) {
    const links = [];
    let cur = h2 ? h2.nextElementSibling : null;
    while (cur) {
      if (cur.tagName === "H2") break;
      cur.querySelectorAll?.("a[href]")?.forEach((a) => {
        const href = a.getAttribute("href");
        if (href) links.push(href);
      });
      cur = cur.nextElementSibling;
    }
    return links;
  }

  function extractDependsLinks(doc, pageUrl) {
    const h2 = findH2(doc, "Depends on");
    if (!h2) return [];
    const rels = collectLinksUntilNextH2(h2);

    // Resolve & filter
    const abs = [];
    for (const href of rels) {
      const u = absUrl(href, pageUrl);
      // typically only within same site
      if (sameOrigin(u)) abs.push(u);
    }
    // unique
    return Array.from(new Set(abs));
  }

  function extractCodeText(doc) {
    // competitive-verifier pages usually have "## Code" then <pre><code>...</code></pre>
    const h2 = findH2(doc, "Code");
    if (!h2) return null;

    let cur = h2.nextElementSibling;
    while (cur) {
      if (cur.tagName === "H2") break;

      // first <pre><code> or <pre>
      const codeEl = cur.querySelector?.("pre code") || cur.querySelector?.("pre");
      if (codeEl) {
        let t = (codeEl.textContent || "").replace(/\r\n/g, "\n").trimEnd();
        // One-level dedent (competitive-verifier often indents code blocks by 4 spaces)
        const lines = t.split("\n");
        const nonEmpty = lines.filter((x) => x.length > 0);
        const allIndented = nonEmpty.length > 0 && nonEmpty.every((x) => x.startsWith("    "));
        if (allIndented) {
          t = lines.map((x) => (x.startsWith("    ") ? x.slice(4) : x)).join("\n").trimEnd();
        }
        return t + "\n";
      }
      cur = cur.nextElementSibling;
    }
    return null;
  }

  function extractTitle(doc) {
    const h1 = doc.querySelector("h1");
    if (h1) return normText(h1.textContent);
    return "";
  }

  // ---------- fetching ----------
  async function fetchPageDoc(url) {
    const res = await fetch(url, { cache: "no-store", credentials: "same-origin" });
    if (!res.ok) throw new Error(`fetch failed: ${res.status} ${url}`);
    const html = await res.text();
    return parseHtml(html);
  }

  // ---------- bundling ----------
  async function bundleFromEntry(entryUrl, opts) {
    const visited = new Set();
    const order = []; // deps first, then the page itself

    async function dfs(url, depth) {
      if (visited.has(url)) return;
      visited.add(url);

      if (opts.maxDepth != null && depth > opts.maxDepth) return;

      const doc = await fetchPageDoc(url);

      // deps first
      const deps = extractDependsLinks(doc, url);
      for (const d of deps) {
        await dfs(d, depth + 1);
      }

      const code = extractCodeText(doc) || "";
      const title = extractTitle(doc) || "";
      order.push({ url, title, code });
    }

    await dfs(entryUrl, 0);

    // stitch
    const parts = [];
    for (const it of order) {
      if (!it.code) continue;
      const path = new URL(it.url).pathname;
      const label = it.title ? `${it.title} (${path})` : path;
      parts.push(`# ===== BEGIN: ${label} =====\n${it.code}# ===== END: ${label} =====\n`);
    }
    return parts.join("\n");
  }

  // ---------- modal UI ----------
  function makeModal(codeText, options) {
    const overlay = document.createElement("div");
    setImp(overlay, "position", "fixed");
    setImp(overlay, "left", "0");
    setImp(overlay, "top", "0");
    setImp(overlay, "width", "100vw");
    setImp(overlay, "height", "100vh");
    setImp(overlay, "margin", "0");
    setImp(overlay, "padding", "1.5vh 1.5vw");
    setImp(overlay, "box-sizing", "border-box");
    setImp(overlay, "background", "rgba(0,0,0,.35)");
    setImp(overlay, "z-index", MAX_Z);
    setImp(overlay, "display", "flex");
    setImp(overlay, "justify-content", "center");
    setImp(overlay, "align-items", "stretch");

    const box = document.createElement("div");
    setImp(box, "width", `min(${options.maxWidthVw}vw, ${options.maxWidthPx}px)`);
    setImp(box, "height", "100%");
    setImp(box, "background", "#fff");
    setImp(box, "border-radius", "10px");
    setImp(box, "box-shadow", "0 10px 30px rgba(0,0,0,.2)");
    setImp(box, "display", "flex");
    setImp(box, "flex-direction", "column");
    setImp(box, "overflow", "hidden");

    // header (sticky)
    const header = document.createElement("div");
    setImp(header, "display", "flex");
    setImp(header, "gap", "8px");
    setImp(header, "align-items", "center");
    setImp(header, "padding", "10px 12px");
    setImp(header, "background", "#fff");
    setImp(header, "border-bottom", "1px solid #e5e5e5");
    setImp(header, "position", "sticky");
    setImp(header, "top", "0");

    const title = document.createElement("div");
    title.textContent = "Bundled code";
    setImp(title, "font-weight", "600");
    setImp(title, "margin-right", "auto");

    const btnCopy = document.createElement("button");
    btnCopy.type = "button";
    btnCopy.textContent = "Copy";
    btnCopy.addEventListener("click", async () => {
      await navigator.clipboard.writeText(codeText);
      btnCopy.textContent = "Copied";
      await sleep(800);
      btnCopy.textContent = "Copy";
    });

    const btnClose = document.createElement("button");
    btnClose.type = "button";
    btnClose.textContent = "Close";

    header.append(title, btnCopy, btnClose);

    // body
    const pre = document.createElement("pre");
    setImp(pre, "margin", "0");
    setImp(pre, "padding", "12px");
    setImp(pre, "flex", "1 1 auto");
    setImp(pre, "overflow", "auto");
    setImp(pre, "background", "#fafafa");

    const code = document.createElement("code");
    code.className = "language-python";
    code.textContent = codeText;

    // No horizontal scroll by default: wrap long lines
    if (options.wrap) {
      setImp(code, "white-space", "pre-wrap");
      setImp(code, "overflow-wrap", "anywhere");
    } else {
      setImp(code, "white-space", "pre");
    }

    pre.appendChild(code);
    box.append(header, pre);
    overlay.appendChild(box);

    function close() {
      overlay.remove();
      document.removeEventListener("keydown", onKeydown, true);
    }

    function onKeydown(e) {
      if (e.key === "Escape") close();
    }

    btnClose.addEventListener("click", close);

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) close();
    });

    // IMPORTANT: append to <html> to avoid sidebar/container effects
    document.documentElement.appendChild(overlay);
    document.addEventListener("keydown", onKeydown, true);

    // Optional highlight.js support (if present)
    if (window.hljs && typeof window.hljs.highlightElement === "function") {
      try {
        window.hljs.highlightElement(code);
      } catch {
        // ignore
      }
    }

    return overlay;
  }

  // ---------- button injection ----------
  function alreadyInjected() {
    return !!document.querySelector("[data-suzlib-bundle-btn='1']");
  }

  function injectBundleButton() {
    if (alreadyInjected()) return;

    const codeH2 = findH2(document, "Code");
    if (!codeH2) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "Bundle";
    btn.setAttribute("data-suzlib-bundle-btn", "1");
    // modest styling that won't clash badly
    btn.style.margin = "8px 0";
    btn.style.padding = "6px 10px";
    btn.style.border = "1px solid #888";
    btn.style.borderRadius = "6px";
    btn.style.background = "#f7f7f7";
    btn.style.cursor = "pointer";

    const note = document.createElement("span");
    note.textContent = " (shows single bundled snippet)";
    note.style.marginLeft = "8px";
    note.style.color = "#666";
    note.style.fontSize = "0.9em";

    const wrap = document.createElement("div");
    wrap.appendChild(btn);
    wrap.appendChild(note);

    codeH2.insertAdjacentElement("afterend", wrap);

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      const old = btn.textContent;
      btn.textContent = "Bundling...";

      try {
        const bundled = await bundleFromEntry(location.href, { maxDepth: 200 });

        makeModal(bundled, {
          wrap: true,       // no horizontal scroll
          maxWidthVw: 98,   // wide
          maxWidthPx: 2400, // cap
        });
      } catch (e) {
        console.error(e);
        alert(String(e && e.message ? e.message : e));
      } finally {
        btn.textContent = old;
        btn.disabled = false;
      }
    });
  }

  // ---------- boot ----------
  // Run once DOM is ready (and also try again shortly in case theme scripts modify DOM)
  function boot() {
    injectBundleButton();
    // some themes may modify after load; retry once
    setTimeout(injectBundleButton, 300);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

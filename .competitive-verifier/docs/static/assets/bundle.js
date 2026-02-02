// suzlib-bundle.js
(() => {
  "use strict";

  const IMP = "important";
  const ZMAX = "2147483647";

  function setImp(el, prop, value) {
    el.style.setProperty(prop, value, IMP);
  }

  function norm(s) {
    return (s || "").replace(/\s+/g, " ").trim();
  }

  function parseHtml(html) {
    return new DOMParser().parseFromString(html, "text/html");
  }

  function headings(doc) {
    return Array.from(doc.querySelectorAll("h2, h3"));
  }

  function findHeading(doc, title) {
    const hs = headings(doc);
    return hs.find((h) => norm(h.textContent) === title) || null;
  }

  function isHeadingTag(tagName) {
    return tagName === "H2" || tagName === "H3";
  }

  // Collect links between a heading and the next heading (h2/h3)
  function collectLinksUntilNextHeading(h) {
    const links = [];
    let cur = h ? h.nextElementSibling : null;
    while (cur) {
      if (isHeadingTag(cur.tagName)) break;
      cur.querySelectorAll?.("a[href]")?.forEach((a) => {
        const href = a.getAttribute("href");
        if (href) links.push(href);
      });
      cur = cur.nextElementSibling;
    }
    return links;
  }

  function sameOrigin(u) {
    try {
      return new URL(u, location.href).origin === location.origin;
    } catch {
      return false;
    }
  }

  function absUrl(href, base) {
    return new URL(href, base).toString();
  }

  async function fetchDoc(url) {
    const res = await fetch(url, { cache: "no-store", credentials: "same-origin" });
    if (!res.ok) throw new Error(`fetch failed: ${res.status} ${url}`);
    return parseHtml(await res.text());
  }

  function extractDepends(doc, pageUrl) {
    const h = findHeading(doc, "Depends on");
    if (!h) return [];
    const rels = collectLinksUntilNextHeading(h);
    const abs = [];
    for (const href of rels) {
      const u = absUrl(href, pageUrl);
      if (sameOrigin(u)) abs.push(u);
    }
    return Array.from(new Set(abs));
  }

  function extractCode(doc) {
    // Prefer: after "Code" heading, find first <pre><code> or <pre>
    const h = findHeading(doc, "Code");
    if (h) {
      let cur = h.nextElementSibling;
      while (cur) {
        if (isHeadingTag(cur.tagName)) break;
        const codeEl = cur.querySelector?.("pre code") || cur.querySelector?.("pre");
        if (codeEl) return normalizeCodeText(codeEl.textContent || "");
        cur = cur.nextElementSibling;
      }
    }
    // Fallback: first <pre><code> on page
    const fallback = doc.querySelector("pre code") || doc.querySelector("pre");
    if (fallback) return normalizeCodeText(fallback.textContent || "");
    return null;
  }

  function normalizeCodeText(t) {
    let s = (t || "").replace(/\r\n/g, "\n").trimEnd();
    // One-level dedent if all non-empty lines start with 4 spaces
    const lines = s.split("\n");
    const nonEmpty = lines.filter((x) => x.length > 0);
    const allIndented = nonEmpty.length > 0 && nonEmpty.every((x) => x.startsWith("    "));
    if (allIndented) {
      s = lines.map((x) => (x.startsWith("    ") ? x.slice(4) : x)).join("\n").trimEnd();
    }
    return s + "\n";
  }

  async function bundleFrom(entryUrl) {
    const visited = new Set();
    const ordered = [];

    async function dfs(url) {
      const abs = absUrl(url, location.href);
      if (visited.has(abs)) return;
      visited.add(abs);

      const doc = await fetchDoc(abs);

      // deps first
      for (const dep of extractDepends(doc, abs)) {
        await dfs(dep);
      }

      const code = extractCode(doc) || "";
      const path = new URL(abs).pathname;
      if (code) {
        ordered.push(`# ===== BEGIN: ${path} =====\n${code}# ===== END: ${path} =====\n`);
      }
    }

    await dfs(entryUrl);
    return ordered.join("\n");
  }

  function makeModal(codeText) {
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
    setImp(overlay, "z-index", ZMAX);
    setImp(overlay, "display", "flex");
    setImp(overlay, "justify-content", "center");
    setImp(overlay, "align-items", "stretch");

    const box = document.createElement("div");
    setImp(box, "width", "min(98vw, 2400px)");   // 横幅を増やす
    setImp(box, "height", "100%");
    setImp(box, "background", "#fff");
    setImp(box, "border-radius", "10px");
    setImp(box, "box-shadow", "0 10px 30px rgba(0,0,0,.2)");
    setImp(box, "display", "flex");
    setImp(box, "flex-direction", "column");
    setImp(box, "overflow", "hidden");

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
      setTimeout(() => (btnCopy.textContent = "Copy"), 900);
    });

    const btnClose = document.createElement("button");
    btnClose.type = "button";
    btnClose.textContent = "Close";

    header.append(title, btnCopy, btnClose);

    const pre = document.createElement("pre");
    setImp(pre, "margin", "0");
    setImp(pre, "padding", "12px");
    setImp(pre, "flex", "1 1 auto");
    setImp(pre, "overflow", "auto");
    setImp(pre, "background", "#fafafa");

    const code = document.createElement("code");
    code.className = "language-python";
    code.textContent = codeText;

    // 横スクロールを避ける（長い行は折る）
    setImp(code, "white-space", "pre-wrap");
    setImp(code, "overflow-wrap", "anywhere");

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

    // 重要：右カラム内ではなく html 直下へ（左サイドバー問題を根絶）
    document.documentElement.appendChild(overlay);
    document.addEventListener("keydown", onKeydown, true);

    // highlight.js が入っているなら自動で効かせる（無ければ何もしない）
    if (window.hljs && typeof window.hljs.highlightElement === "function") {
      try {
        window.hljs.highlightElement(code);
      } catch {
        // ignore
      }
    }
  }

  function injectBundleButton() {
    if (document.querySelector("[data-suzlib-bundle='1']")) return;

    // Prefer to inject right after "Code" heading if exists; otherwise before first <pre>
    const h = findHeading(document, "Code");
    const pre = document.querySelector("pre");
    if (!h && !pre) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "Bundle";
    btn.setAttribute("data-suzlib-bundle", "1");
    btn.style.margin = "8px 0";
    btn.style.padding = "6px 10px";
    btn.style.border = "1px solid #888";
    btn.style.borderRadius = "6px";
    btn.style.background = "#f7f7f7";
    btn.style.cursor = "pointer";

    const place = h ? h : pre;
    place.insertAdjacentElement("afterend", btn);

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      const old = btn.textContent;
      btn.textContent = "Bundling...";
      try {
        const bundled = await bundleFrom(location.href);
        makeModal(bundled);
      } catch (e) {
        console.error(e);
        alert(String(e && e.message ? e.message : e));
      } finally {
        btn.textContent = old;
        btn.disabled = false;
      }
    });
  }

  function boot() {
    injectBundleButton();
    // テーマ側が後からDOMをいじる場合に備えて1回だけリトライ
    setTimeout(injectBundleButton, 300);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

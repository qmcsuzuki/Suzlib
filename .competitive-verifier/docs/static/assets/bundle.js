// bundle.js
(() => {
  "use strict";

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

  function stripInternalImports(codeText) {
    const lines = (codeText || "").replace(/\r\n/g, "\n").split("\n");
    const out = [];

    const parenDelta = (s) => (s.match(/\(/g) || []).length - (s.match(/\)/g) || []).length;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];

      // internal imports: "from python.... import ..." or "import python...."
      const m = line.match(
        /^(\s*)(?:from\s+(python(?:\.[A-Za-z0-9_]+)*)\s+import\b|import\s+(python(?:\.[A-Za-z0-9_]+)*)(?:\s|$))/
      );

      if (!m) {
        out.push(line);
        continue;
      }

      const indent = m[1] || "";
      const trimmed = line.trim();

      // Keep syntax valid even inside blocks
      if (indent.length === 0) out.push(`# [bundled] ${trimmed}`);
      else out.push(`${indent}pass  # [bundled] ${trimmed}`);

      // Skip multiline import blocks: parentheses / backslash continuation
      let depth = parenDelta(line);
      while (depth > 0 && i + 1 < lines.length) {
        i++;
        line = lines[i];
        depth += parenDelta(line);
      }
      while (line.trimEnd().endsWith("\\") && i + 1 < lines.length) {
        i++;
        line = lines[i];
      }
    }

    return out.join("\n");
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
      const pageUrl = abs.split(/[?#]/, 1)[0];
      if (code) {
        ordered.push(`# ===== BEGIN: ${pageUrl} =====\n${code}# ===== END: ${pageUrl} =====\n`);
      }
    }

    await dfs(entryUrl);
    return stripInternalImports(ordered.join("\n"));
  }

  function makeModal(codeText) {
    const overlay = document.createElement("div");
    overlay.className = "suz-bundle-overlay";

    const box = document.createElement("div");
    box.className = "suz-bundle-dialog";

    const header = document.createElement("div");
    header.className = "suz-bundle-header";

    const title = document.createElement("div");
    title.className = "suz-bundle-title";
    title.textContent = "Bundled code";

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
    pre.className = "suz-bundle-pre";

    const code = document.createElement("code");
    code.className = "language-python suz-bundle-code";
    code.textContent = codeText;

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
    btn.style.margin = "0";
    btn.style.padding = "6px 10px";
    btn.style.border = "1px solid #888";
    btn.style.borderRadius = "6px";
    btn.style.background = "#f7f7f7";
    btn.style.cursor = "pointer";

    const toolbar = document.createElement("div");
    toolbar.style.cssText = "display:flex; flex-wrap:wrap; align-items:center; gap:8px 24px; margin:8px 0";
    const secondary = document.createElement("div");
    secondary.style.cssText = "display:flex; align-items:center; margin-left:auto";
    secondary.appendChild(btn);
    (h || pre).insertAdjacentElement(h ? "afterend" : "beforebegin", toolbar);

    const bundleCopy = document.createElement("button");
    bundleCopy.type = "button";
    bundleCopy.textContent = "Bundle and Copy";
    bundleCopy.style.cssText = btn.style.cssText;
    bundleCopy.style.background = "#1756a9";
    bundleCopy.style.borderColor = "#1756a9";
    bundleCopy.style.color = "#fff";
    bundleCopy.style.fontWeight = "600";
    toolbar.append(bundleCopy, secondary);

    bundleCopy.addEventListener("click", async () => {
      bundleCopy.disabled = true;
      bundleCopy.textContent = "Bundling...";
      try {
        const bundled = bundleFrom(location.href);
        if (window.ClipboardItem && navigator.clipboard?.write) {
          // Safari でもクリック中にコピーを開始し、本文は取得後に渡す。
          const data = bundled.then(text => new Blob([text], { type: "text/plain" }));
          await navigator.clipboard.write([new ClipboardItem({ "text/plain": data })]);
        } else {
          await navigator.clipboard.writeText(await bundled);
        }
        bundleCopy.textContent = "Copied!";
        setTimeout(() => {
          bundleCopy.textContent = "Bundle and Copy";
          bundleCopy.disabled = false;
        }, 1000);
      } catch (e) {
        bundleCopy.textContent = "Bundle and Copy";
        bundleCopy.disabled = false;
        alert(String(e.message || e));
      }
    });

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

  function highlightPageCode() {
  if (!window.hljs || typeof window.hljs.highlightElement !== "function") return;

  // 既存のコード（ページの Code セクション等）
  document.querySelectorAll("pre code").forEach((code) => {
    if (code.dataset.suzHlDone === "1") return;

    // 言語が付いていない場合、python をデフォルトにしておく（好みで変更可）
    if (!code.className || !/language-/.test(code.className)) {
      code.classList.add("language-python");
    }

    try {
      window.hljs.highlightElement(code);
      code.dataset.suzHlDone = "1";
    } catch {
      // 無視
    }
  });
  }

  function setupCopyButton() {
    const bundle = document.querySelector("[data-suzlib-bundle='1']");
    const copy = document.querySelector("button.code-copy-btn");
    if (!bundle || !copy || copy.dataset.suzCopyFix === "1") return;

    // 標準の Copy ボタンを移動する前に、対応するコード領域を保持する。
    const codeArea = copy.closest(".code");
    if (!codeArea) return;
    copy.dataset.suzCopyFix = "1";
    bundle.insertAdjacentElement("afterend", copy);

    Object.assign(copy.style, {
      padding: bundle.style.padding,
      border: bundle.style.border,
      borderRadius: bundle.style.borderRadius,
      background: bundle.style.background,
      cursor: bundle.style.cursor,
      margin: "0 0 0 8px",
    });

    function fallbackCopy(text) {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }

    copy.addEventListener("click", (e) => {
      e.preventDefault();
      // 標準ハンドラは移動後の closest('.code') を参照できないため実行しない。
      e.stopImmediatePropagation();
      const code = codeArea.querySelector("pre:not(.disable) code");
      const text = code?.textContent || "";
      if (!text) return;

      if (navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
      } else {
        fallbackCopy(text);
      }
    }, true);
  }

  function boot() {
    injectBundleButton();
    highlightPageCode();
    setupCopyButton();
    // テーマ側の遅延した DOM 生成に備えて一度だけ再試行する。
    setTimeout(() => {
      injectBundleButton();
      setupCopyButton();
    }, 300);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

// /assets/bundle.js

(function () {
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // ページHTMLからコードを抽出（competitive-verifier のページは "## Code" の直後に pre が来る想定）
  function extractCodeFromHtml(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    // よくある構造：<pre><code>...</code></pre>
    const codeEl = doc.querySelector("pre code") || doc.querySelector("pre");
    if (!codeEl) return null;
    return codeEl.textContent.replace(/\r\n/g, "\n");
  }

  // `from python.a.b.C import X` / `import python.a.b.C` を拾う（必要なら拡張）
  function parseInternalImports(code) {
    const deps = new Set();
    const lines = code.split("\n");
    for (const line of lines) {
      // from python.xxx.yyy import Z
      let m = line.match(/^\s*from\s+(python(?:\.[A-Za-z0-9_]+)+)\s+import\s+/);
      if (m) deps.add(m[1]);
      // import python.xxx.yyy
      m = line.match(/^\s*import\s+(python(?:\.[A-Za-z0-9_]+)+)\s*$/);
      if (m) deps.add(m[1]);
    }
    return [...deps];
  }

  // module "python.data_structure.array1D.FenwickTree" -> "/Suzlib/python/data_structure/array1D/FenwickTree.py"
  function moduleToUrl(mod) {
    const base = document.querySelector('meta[name="baseurl"]')?.content || ""; // 無ければ空
    // Jekyll の relative_url をJSで再現するのは面倒なので、ここでは location から推定：
    // site が /Suzlib/ 以下なら pathname の先頭2要素を採用して prefix を作る
    const parts = location.pathname.split("/").filter(Boolean);
    const prefix = parts.length >= 1 ? ("/" + parts[0]) : "";
    return prefix + "/" + mod.replace(/\./g, "/") + ".py";
  }

  async function fetchCode(url) {
    const res = await fetch(url, { cache: "force-cache" });
    if (!res.ok) throw new Error(`fetch failed: ${url} (${res.status})`);
    const html = await res.text();
    const code = extractCodeFromHtml(html);
    if (code == null) throw new Error(`code not found in: ${url}`);
    return code;
  }

  // 依存を DFS で並べる（重複排除、依存→本体の順）
  async function bundleFromEntryUrl(entryUrl) {
    const visited = new Set();
    const ordered = []; // url のトポロジカル順（依存が先）

    async function dfsUrl(url) {
      if (visited.has(url)) return;
      visited.add(url);

      const code = await fetchCode(url);
      const mods = parseInternalImports(code);
      for (const mod of mods) {
        const depUrl = moduleToUrl(mod);
        await dfsUrl(depUrl);
      }
      ordered.push({ url, code });
    }

    await dfsUrl(entryUrl);
    return ordered;
  }

  function ensureUi() {
    // "Code" 見出し付近にボタンを置く（雑に pre の直前に置く）
    const pre = document.querySelector("pre");
    if (!pre) return null;

    const wrap = document.createElement("div");
    wrap.style.display = "flex";
    wrap.style.gap = "8px";
    wrap.style.margin = "12px 0";

    const btn = document.createElement("button");
    btn.textContent = "Bundle";
    btn.type = "button";

    const out = document.createElement("div");
    out.style.marginTop = "12px";

    wrap.appendChild(btn);
    pre.parentNode.insertBefore(wrap, pre);
    pre.parentNode.insertBefore(out, pre);

    return { btn, out };
  }

  function highlightCodeBlocks(root = document) {
    if (!window.hljs) return;
    root.querySelectorAll("pre code").forEach(block => {
      window.hljs.highlightElement(block);
    });
  }

  // class / def 直下の docstring を雑に抽出して一覧化
  function extractPythonDocEntries(code) {
    const entries = [];
    const lines = code.split("\n");

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const m = line.match(/^(\s*)(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b/);
      if (!m) continue;

      const baseIndent = m[1].length;
      const name = m[2];

      // 次の有効行を探す
      let j = i + 1;
      while (j < lines.length && lines[j].trim() === "") j++;
      if (j >= lines.length) continue;

      const next = lines[j];
      const nextIndent = (next.match(/^\s*/) || [""])[0].length;
      if (nextIndent <= baseIndent) continue;

      const tripleMatch = next.match(/^\s*(["']{3})(.*)$/);
      if (!tripleMatch) continue;

      const quote = tripleMatch[1];
      let body = tripleMatch[2];

      if (body.includes(quote)) {
        body = body.split(quote)[0];
      } else {
        const chunks = [body];
        j++;
        while (j < lines.length) {
          const ln = lines[j];
          const idx = ln.indexOf(quote);
          if (idx !== -1) {
            chunks.push(ln.slice(0, idx));
            break;
          }
          chunks.push(ln);
          j++;
        }
        body = chunks.join("\n");
      }

      const text = body.replace(/^\s*\n/, "").replace(/\s+$/, "");
      if (!text) continue;
      entries.push({ name, text });
    }

    return entries;
  }

  function renderDocEntries(entries, root = document) {
    if (!entries.length) return;

    const pre = root.querySelector("pre");
    if (!pre || !pre.parentNode) return;

    const section = document.createElement("section");
    section.style.margin = "20px 0";
    section.innerHTML = `<h2>Docs</h2>`;

    for (const entry of entries) {
      const block = document.createElement("details");
      block.style.margin = "8px 0";
      block.innerHTML = `
        <summary><code>${escapeHtml(entry.name)}</code></summary>
        <pre><code>${escapeHtml(entry.text)}</code></pre>
      `;
      section.appendChild(block);
    }

    pre.parentNode.insertBefore(section, pre);
    highlightCodeBlocks(section);
  }

  async function onBundleClick(out) {
    out.innerHTML = "Bundling...";
    try {
      const entryUrl = location.pathname; // このページ自体（.py だが HTML）
      const items = await bundleFromEntryUrl(entryUrl);

      // import 行は二重になりやすいので、内部 import は削って見やすくする（必要ならOFFに）
      const cleaned = items.map(({ url, code }) => {
        const lines = code.split("\n").filter(line =>
          !line.match(/^\s*from\s+python\./) && !line.match(/^\s*import\s+python\./)
        );
        return { url, code: lines.join("\n") };
      });

      const bundled =
        cleaned.map(x => `# ===== ${x.url} =====\n${x.code}\n`).join("\n");

      out.innerHTML = `
        <div style="margin:8px 0;">
          <button type="button" id="bundle-copy">Copy bundled code</button>
        </div>
        <pre><code>${escapeHtml(bundled)}</code></pre>
      `;
      highlightCodeBlocks(out);
      out.querySelector("#bundle-copy").addEventListener("click", async () => {
        await navigator.clipboard.writeText(bundled);
      });
    } catch (e) {
      out.textContent = String(e);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    highlightCodeBlocks();

    const codeEl = document.querySelector("pre code") || document.querySelector("pre");
    if (codeEl) {
      const entries = extractPythonDocEntries(codeEl.textContent || "");
      renderDocEntries(entries);
    }

    const ui = ensureUi();
    if (!ui) return;
    ui.btn.addEventListener("click", () => onBundleClick(ui.out));
  });
})();

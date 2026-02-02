// /assets/suzlib-bundle.js
(() => {
  function textOf(el) { return (el?.textContent || "").trim(); }

  function findH2ByText(target) {
    const hs = Array.from(document.querySelectorAll("h2"));
    return hs.find(h => textOf(h) === target) || null;
  }

  function collectSectionListLinks(h2) {
    // h2 の次に来る ul / ol を拾う（次の h2 まで）
    const links = [];
    let cur = h2?.nextElementSibling;
    while (cur) {
      if (cur.tagName === "H2") break;
      if (cur.tagName === "UL" || cur.tagName === "OL") {
        cur.querySelectorAll("a[href]").forEach(a => links.push(a.getAttribute("href")));
      }
      cur = cur.nextElementSibling;
    }
    return links;
  }

  function extractCodeBlockTextFromDoc(doc) {
    // 「## Code」直下の pre > code を探す
    const hs = Array.from(doc.querySelectorAll("h2"));
    const codeH2 = hs.find(h => textOf(h) === "Code");
    if (!codeH2) return null;

    let cur = codeH2.nextElementSibling;
    while (cur) {
      if (cur.tagName === "H2") break;
      const code = cur.querySelector?.("pre code") || (cur.matches?.("pre code") ? cur : null);
      if (code) {
        let t = code.textContent.replace(/\r\n/g, "\n");

        // competitive-verifier の出力は各行が 4 スペースインデントされることが多いので、1段だけ剥がす
        const lines = t.split("\n");
        const stripped = lines.map(line => line.startsWith("    ") ? line.slice(4) : line);
        return stripped.join("\n").trimEnd() + "\n";
      }
      cur = cur.nextElementSibling;
    }
    return null;
  }

  async function fetchDoc(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error(`fetch failed: ${url} (${res.status})`);
    const html = await res.text();
    return new DOMParser().parseFromString(html, "text/html");
  }

  async function dfsBundle(startUrl) {
    const seen = new Set();
    const out = [];

    async function dfs(url) {
      // url を正規化（相対→絶対）
      const abs = new URL(url, location.href).toString();
      if (seen.has(abs)) return;
      seen.add(abs);

      const doc = await fetchDoc(abs);

      // 先に依存を処理（依存→本体の順で並べたい場合）
      const depH2 = Array.from(doc.querySelectorAll("h2")).find(h => textOf(h) === "Depends on");
      if (depH2) {
        const depLinks = collectSectionListLinks(depH2);
        for (const href of depLinks) await dfs(new URL(href, abs).toString());
      }

      const code = extractCodeBlockTextFromDoc(doc);
      if (code) {
        // 区切りコメントを入れる（好みで消してOK）
        const path = new URL(abs).pathname;
        out.push(`# ---- from ${path} ----\n` + code);
      }
    }

    await dfs(startUrl);
    return out.join("\n");
  }

function makeModal(codeText) {
  // overlay (full viewport)
  const overlay = document.createElement("div");

  // orderedlist テーマの2カラムに影響されないよう、important 付きで強制
  const setImp = (el, prop, value) => el.style.setProperty(prop, value, "important");

  setImp(overlay, "position", "fixed");
  setImp(overlay, "left", "0");
  setImp(overlay, "top", "0");
  setImp(overlay, "width", "100vw");
  setImp(overlay, "height", "100vh");
  setImp(overlay, "margin", "0");
  setImp(overlay, "padding", "1.5vh 1.5vw");
  setImp(overlay, "box-sizing", "border-box");
  setImp(overlay, "background", "rgba(0,0,0,.35)");
  setImp(overlay, "z-index", "2147483647");
  setImp(overlay, "display", "flex");
  setImp(overlay, "justify-content", "center");
  setImp(overlay, "align-items", "stretch");

  // modal box (wide)
  const box = document.createElement("div");
  setImp(box, "width", "min(98vw, 2200px)");  // 横幅を増やす（上限は好みで）
  setImp(box, "height", "100%");
  setImp(box, "background", "#fff");
  setImp(box, "border-radius", "10px");
  setImp(box, "box-shadow", "0 10px 30px rgba(0,0,0,.2)");
  setImp(box, "display", "flex");
  setImp(box, "flex-direction", "column");
  setImp(box, "overflow", "hidden");

  // header (copy button at top)
  const header = document.createElement("div");
  setImp(header, "display", "flex");
  setImp(header, "gap", "8px");
  setImp(header, "align-items", "center");
  setImp(header, "padding", "10px 12px");
  setImp(header, "background", "#fff");
  setImp(header, "border-bottom", "1px solid #e5e5e5");
  // スクロールしても上に残す
  setImp(header, "position", "sticky");
  setImp(header, "top", "0");

  const btnCopy = document.createElement("button");
  btnCopy.type = "button";
  btnCopy.textContent = "Copy bundled code";
  btnCopy.addEventListener("click", async () => {
    await navigator.clipboard.writeText(codeText);
    btnCopy.textContent = "Copied";
    setTimeout(() => (btnCopy.textContent = "Copy bundled code"), 900);
  });

  const btnClose = document.createElement("button");
  btnClose.type = "button";
  btnClose.textContent = "Close";
  btnClose.addEventListener("click", () => overlay.remove());

  header.append(btnCopy, btnClose);

  // code area
  const pre = document.createElement("pre");
  setImp(pre, "margin", "0");
  setImp(pre, "padding", "12px");
  setImp(pre, "flex", "1 1 auto");
  setImp(pre, "overflow", "auto");
  setImp(pre, "background", "#fafafa");

  const code = document.createElement("code");
  code.className = "language-python";
  code.textContent = codeText;

  // 横スクロール不要：折り返し
  setImp(code, "white-space", "pre-wrap");
  setImp(code, "overflow-wrap", "anywhere");

  pre.appendChild(code);

  box.append(header, pre);
  overlay.appendChild(box);

  // 背景クリックで閉じる
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.remove();
  });

  // 重要：右カラム内ではなく html 直下へ（左サイドバー問題を根絶）
  document.documentElement.appendChild(overlay);

  // highlight.js が入っている場合だけハイライト（後述）
  if (window.hljs && typeof window.hljs.highlightElement === "function") {
    window.hljs.highlightElement(code);
  }

  return overlay;
}

  
  function injectBundleButton() {
    // 「## Code」見出しの近くに置く
    const codeH2 = findH2ByText("Code");
    if (!codeH2) return;

    const btn = document.createElement("button");
    btn.textContent = "Bundle";
    btn.style.cssText = "margin:8px 0;padding:6px 10px;border:1px solid #888;border-radius:6px;background:#f7f7f7;cursor:pointer;";
    btn.onclick = async () => {
      btn.disabled = true;
      btn.textContent = "Bundling...";
      try {
        const bundled = await dfsBundle(location.href);
        document.body.append(makeModal(bundled));
        btn.textContent = "Bundle";
      } catch (e) {
        console.error(e);
        btn.textContent = "Bundle (failed; see console)";
      } finally {
        btn.disabled = false;
      }
    };

    codeH2.insertAdjacentElement("afterend", btn);
  }

  window.addEventListener("DOMContentLoaded", injectBundleButton);
})();

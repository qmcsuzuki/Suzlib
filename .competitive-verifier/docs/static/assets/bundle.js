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

function makeModal(text) {
  const bg = document.createElement("div");
  // 重要: 既存CSSの影響を極力受けないよう、必要なプロパティを明示
  bg.style.position = "fixed";
  bg.style.top = "0";
  bg.style.left = "0";
  bg.style.width = "100vw";
  bg.style.height = "100vh";
  bg.style.margin = "0";
  bg.style.padding = "2vh 2vw";
  bg.style.boxSizing = "border-box";
  bg.style.background = "rgba(0,0,0,.35)";
  bg.style.zIndex = "2147483647"; // ほぼ最上位
  bg.style.display = "flex";
  bg.style.justifyContent = "center";
  bg.style.alignItems = "stretch";

  const box = document.createElement("div");
  // 横幅を最大化（必要なら 1800px をさらに上げてOK）
  box.style.width = "min(96vw, 1800px)";
  box.style.height = "100%";
  box.style.background = "#fff";
  box.style.borderRadius = "10px";
  box.style.boxShadow = "0 10px 30px rgba(0,0,0,.2)";
  box.style.display = "flex";
  box.style.flexDirection = "column";
  box.style.overflow = "hidden";

  const header = document.createElement("div");
  // Copy ボタンを常に上に固定
  header.style.display = "flex";
  header.style.gap = "8px";
  header.style.alignItems = "center";
  header.style.padding = "10px 12px";
  header.style.borderBottom = "1px solid #e5e5e5";
  header.style.background = "#fff";
  header.style.flex = "0 0 auto";

  const copy = document.createElement("button");
  copy.type = "button";
  copy.textContent = "Copy bundled code";
  copy.onclick = async () => {
    await navigator.clipboard.writeText(text);
    copy.textContent = "Copied";
    setTimeout(() => (copy.textContent = "Copy bundled code"), 900);
  };

  const close = document.createElement("button");
  close.type = "button";
  close.textContent = "Close";
  close.onclick = () => bg.remove();

  header.append(copy, close);

  const pre = document.createElement("pre");
  pre.style.margin = "0";
  pre.style.padding = "12px";
  pre.style.flex = "1 1 auto";
  pre.style.overflow = "auto";
  pre.style.background = "#fafafa";
  pre.style.boxSizing = "border-box";

  const code = document.createElement("code");
  code.className = "language-python";
  code.textContent = text;

  // 横スクロールを避けたい場合（インデントは維持しつつ長い行だけ折る）
  code.style.whiteSpace = "pre-wrap";
  code.style.overflowWrap = "anywhere";

  pre.appendChild(code);
  box.append(header, pre);
  bg.appendChild(box);

  // 背景クリックで閉じる
  bg.addEventListener("click", (e) => {
    if (e.target === bg) bg.remove();
  });

  // ここが超重要: body ではなく html 直下に刺す（transform 罠を回避）
  document.documentElement.appendChild(bg);

  // highlight.js が入っているならハイライト（無ければ何もしない）
  if (window.hljs && typeof window.hljs.highlightElement === "function") {
    window.hljs.highlightElement(code);
  }

  return bg;
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

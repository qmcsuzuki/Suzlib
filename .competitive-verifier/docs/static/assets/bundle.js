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
  bg.style.cssText =
    "position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:9999;padding:2vh 2vw;";

  const box = document.createElement("div");
  // 横幅を大きく（以前の体感に寄せるなら max-width を上げる/ほぼvwにする）
  box.style.cssText =
    "background:#fff;width:min(98vw,1600px);margin:0 auto;padding:14px;border-radius:10px;" +
    "box-shadow:0 10px 30px rgba(0,0,0,.2);height:96vh;display:flex;flex-direction:column;gap:10px;";

  const row = document.createElement("div");
  // Copy を上に配置（常に見える）
  row.style.cssText = "display:flex;gap:8px;align-items:center;position:sticky;top:0;background:#fff;padding-bottom:6px;";

  const copy = document.createElement("button");
  copy.textContent = "Copy bundled code";
  copy.type = "button";
  copy.onclick = async () => {
    await navigator.clipboard.writeText(text);
    copy.textContent = "Copied";
    setTimeout(() => (copy.textContent = "Copy bundled code"), 900);
  };

  const close = document.createElement("button");
  close.textContent = "Close";
  close.type = "button";
  close.onclick = () => bg.remove();

  row.append(copy, close);

  // 表示は pre/code に（ハイライト可能、CSSで折り返しも制御可能）
  const pre = document.createElement("pre");
  pre.style.cssText =
    "margin:0;flex:1;overflow:auto;border:1px solid #ddd;border-radius:8px;padding:10px;" +
    "background:#fafafa;";

  const code = document.createElement("code");
  code.className = "language-python";
  code.textContent = text;

  // 横スクロール不要にしたいなら折り返しを有効化
  // （インデントは維持しつつ、長い1行だけを折る）
  code.style.whiteSpace = "pre-wrap";
  code.style.overflowWrap = "anywhere"; // 長いトークンも折る
  code.style.wordBreak = "break-word";

  pre.appendChild(code);

  box.append(row, pre);
  bg.append(box);

  // 背景クリックで閉じる
  bg.addEventListener("click", (e) => {
    if (e.target === bg) bg.remove();
  });

  // highlight.js が入っていればハイライト（入っていなければ何もしない）
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

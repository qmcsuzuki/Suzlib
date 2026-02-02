import { bundlePythonSnippet } from "./snippet-bundler.js";

function normalizePythonPath(pathname) {
  const pythonIndex = pathname.indexOf("/python/");
  if (pythonIndex >= 0) {
    return pathname.slice(pythonIndex + 1);
  }
  return pathname.startsWith("/") ? pathname.slice(1) : pathname;
}

function inferPathFromLink(link) {
  if (!link) {
    return null;
  }
  try {
    const url = new URL(link.href, window.location.origin);
    const blobIndex = url.pathname.indexOf("/blob/");
    if (blobIndex >= 0) {
      const pathPart = url.pathname.slice(blobIndex + "/blob/".length);
      const segments = pathPart.split("/").slice(1);
      const filePath = segments.join("/");
      return normalizePythonPath(filePath);
    }
    if (url.pathname.endsWith(".py")) {
      return normalizePythonPath(url.pathname);
    }
  } catch (error) {
    return null;
  }
  return null;
}

function inferPathFromLocation() {
  const match = window.location.pathname.match(/\/(python\/.*)\.(html|md)?$/);
  if (!match) {
    return null;
  }
  return `${match[1]}.py`;
}

function resolveSnippetPath(container) {
  const direct =
    container.getAttribute("data-snippet-path") ||
    container.getAttribute("data-file-path") ||
    container.getAttribute("data-path");
  if (direct) {
    if (direct.endsWith(".py")) {
      return direct;
    }
    if (direct.startsWith("python/")) {
      return `${direct}.py`;
    }
  }

  const link =
    container.querySelector('a[href*="/blob/"]') ||
    container.querySelector('a[href$=".py"]');
  const inferred = inferPathFromLink(link);
  if (inferred) {
    return inferred;
  }

  const fallbackLink = document.querySelector('a[href$=".py"]');
  if (fallbackLink) {
    const fallbackPath = inferPathFromLink(fallbackLink);
    if (fallbackPath) {
      return fallbackPath;
    }
  }

  return inferPathFromLocation();
}

function createBundleControls() {
  const wrapper = document.createElement("div");
  wrapper.className = "snippet-bundle-controls";

  const button = document.createElement("button");
  button.type = "button";
  button.className = "snippet-bundle-button";
  button.textContent = "Bundle";

  const status = document.createElement("span");
  status.className = "snippet-bundle-status";

  const output = document.createElement("textarea");
  output.className = "snippet-bundle-output";
  output.rows = 16;
  output.readOnly = true;

  wrapper.append(button, status);
  return { wrapper, button, status, output };
}

async function handleBundleClick({ button, status, output, filePath }) {
  button.disabled = true;
  status.textContent = "Bundling...";
  output.value = "";

  try {
    const bundled = await bundlePythonSnippet(filePath);
    output.value = bundled;
    status.textContent = "Bundled";
  } catch (error) {
    status.textContent = "Failed to bundle";
    output.value = error instanceof Error ? error.message : String(error);
  } finally {
    button.disabled = false;
  }
}

function attachBundleUI(snippetContainer) {
  if (snippetContainer.dataset.bundleAttached === "true") {
    return;
  }
  const filePath = resolveSnippetPath(snippetContainer);
  if (!filePath) {
    return;
  }

  const codeBlock = snippetContainer.querySelector("pre");
  if (!codeBlock) {
    return;
  }

  const { wrapper, button, status, output } = createBundleControls();
  snippetContainer.insertBefore(wrapper, codeBlock);
  snippetContainer.insertBefore(output, codeBlock.nextSibling);

  button.addEventListener("click", () =>
    handleBundleClick({ button, status, output, filePath })
  );

  snippetContainer.dataset.bundleAttached = "true";
}

function findSnippetContainers() {
  const candidates = new Set();
  document.querySelectorAll("[data-snippet-path], [data-file-path], [data-path]").forEach((el) =>
    candidates.add(el)
  );
  document.querySelectorAll("pre").forEach((pre) => {
    if (pre.parentElement) {
      candidates.add(pre.parentElement);
    }
  });
  return Array.from(candidates);
}

function applyBundleUI() {
  const containers = findSnippetContainers();
  containers.forEach((container) => attachBundleUI(container));
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", applyBundleUI);
} else {
  applyBundleUI();
}

const PYTHON_IMPORT_RE = /^\s*from\s+python\.([A-Za-z0-9_.]+)\s+import\s+([A-Za-z0-9_.*,\s]+)\s*$/gm;

function pathFromPythonImport(importPath) {
  return `python/${importPath.replace(/\./g, "/")}.py`;
}

export function extractPythonImports(code) {
  const matches = [];
  let match;
  while ((match = PYTHON_IMPORT_RE.exec(code)) !== null) {
    matches.push(match[1]);
  }
  return matches;
}

export function stripDependencyImports(code) {
  return code.replace(PYTHON_IMPORT_RE, "");
}

function inferRepoInfo() {
  const ownerMeta = document.querySelector('meta[name="github-owner"]');
  const repoMeta = document.querySelector('meta[name="github-repo"]');
  const branchMeta = document.querySelector('meta[name="github-branch"]');
  if (ownerMeta && repoMeta) {
    return {
      owner: ownerMeta.content,
      repo: repoMeta.content,
      branch: branchMeta ? branchMeta.content : "main",
    };
  }

  const { hostname, pathname } = window.location;
  if (!hostname.endsWith("github.io")) {
    return null;
  }
  const owner = hostname.split(".")[0];
  const repo = pathname.split("/")[1];
  if (!repo) {
    return null;
  }
  return { owner, repo, branch: "main" };
}

export function buildRawBaseUrl(options = {}) {
  if (options.rawBaseUrl) {
    return options.rawBaseUrl.replace(/\/+$/, "") + "/";
  }
  const info = inferRepoInfo();
  if (!info) {
    return null;
  }
  const branch = options.branch || info.branch || "main";
  return `https://raw.githubusercontent.com/${info.owner}/${info.repo}/${branch}/`;
}

export async function fetchPythonFile(filePath, options = {}) {
  const baseUrl = buildRawBaseUrl(options);
  if (!baseUrl) {
    throw new Error("Unable to determine raw GitHub URL base.");
  }
  const response = await fetch(`${baseUrl}${filePath}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${filePath}: ${response.status}`);
  }
  return response.text();
}

export async function bundlePythonSnippet(entryFilePath, options = {}) {
  const visited = new Set();
  const chunks = [];

  async function visit(filePath) {
    if (visited.has(filePath)) {
      return;
    }
    visited.add(filePath);
    const content = await fetchPythonFile(filePath, options);
    const imports = extractPythonImports(content).map(pathFromPythonImport);
    for (const dependency of imports) {
      await visit(dependency);
    }
    const stripped = stripDependencyImports(content).trimEnd();
    if (stripped.length > 0) {
      chunks.push(stripped);
    }
  }

  await visit(entryFilePath);
  return chunks.join("\n\n");
}

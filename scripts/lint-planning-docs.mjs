import { readdirSync, existsSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath, URL } from "node:url";

const root = process.cwd();
const planningRoot = join(root, "_bmad-output");

function markdownFiles(directory) {
  if (!existsSync(directory)) return [];
  const files = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...markdownFiles(path));
    else if (entry.isFile() && path.endsWith(".md"))
      files.push(relative(root, path).split(sep).join("/"));
  }
  return files.sort();
}

const files = markdownFiles(planningRoot);
if (files.length === 0) {
  console.log("Planning-document lint skipped: no _bmad-output Markdown files exist.");
  process.exit(0);
}

const cliEntrypoints = {
  "markdownlint-cli2": fileURLToPath(
    new URL("markdownlint-cli2-bin.mjs", import.meta.resolve("markdownlint-cli2")),
  ),
  cspell: fileURLToPath(import.meta.resolve("cspell/bin")),
};

for (const [command, entrypoint] of Object.entries(cliEntrypoints)) {
  // The append-only BMAD memlog is an internal session trace, not a canonical
  // planning document; do not lint its free-form evidence as planning prose.
  const planningFiles = files.filter((file) => !file.endsWith(".memlog.md"));
  const args =
    command === "markdownlint-cli2"
      ? planningFiles
      : ["--no-progress", "--no-summary", ...planningFiles];
  // Run the pinned local CLI with Node; Windows cannot spawn pnpm's .cmd shim
  // without a shell. Keep document paths as literal arguments on every platform.
  const result = spawnSync(process.execPath, [entrypoint, ...args], {
    cwd: root,
    stdio: "inherit",
    shell: false,
  });
  if (result.error) {
    console.error(`Unable to run ${command}: ${result.error.message}`);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}

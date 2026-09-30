import { readdirSync, existsSync } from "node:fs";
import { join, relative } from "node:path";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const planningRoot = join(root, "_bmad-output");

function markdownFiles(directory) {
  if (!existsSync(directory)) return [];
  const files = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...markdownFiles(path));
    else if (entry.isFile() && path.endsWith(".md")) files.push(relative(root, path));
  }
  return files.sort();
}

const files = markdownFiles(planningRoot);
if (files.length === 0) {
  console.log("Planning-document lint skipped: no _bmad-output Markdown files exist.");
  process.exit(0);
}

for (const command of ["markdownlint-cli2", "cspell"]) {
  // The append-only BMAD memlog is an internal session trace, not a canonical
  // planning document; do not lint its free-form evidence as planning prose.
  const planningFiles = files.filter((file) => !file.endsWith(".memlog.md"));
  const args =
    command === "markdownlint-cli2"
      ? planningFiles
      : ["--no-progress", "--no-summary", ...planningFiles];
  const result = spawnSync("pnpm", ["exec", command, ...args], {
    cwd: root,
    stdio: "inherit",
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

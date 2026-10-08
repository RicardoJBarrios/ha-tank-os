import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const mode = process.argv[2];
const roots = ["src", "custom_components", "tests"].filter(existsSync);

function containsPythonFile(path) {
  return readdirSync(path).some((entry) => {
    const child = join(path, entry);
    const stats = statSync(child);
    return stats.isDirectory() ? containsPythonFile(child) : child.endsWith(".py");
  });
}

function run(command, args) {
  const result = spawnSync(command, args, { stdio: "inherit", shell: false });
  if (result.error) {
    console.error(`Unable to run ${command}: ${result.error.message}`);
    process.exit(1);
  }
  process.exit(result.status ?? 1);
}

if (!mode || !["typecheck", "security", "dependencies"].includes(mode)) {
  console.error("Usage: node scripts/run-python-quality.mjs <typecheck|security|dependencies>");
  process.exit(2);
}

if (mode === "dependencies") {
  const dependencyFiles = ["requirements.txt"].filter(existsSync);
  if (dependencyFiles.length === 0) {
    console.log(
      "Python product dependency audit skipped: no product requirements file exists yet.",
    );
    process.exit(0);
  }
  run("pip-audit", [
    "--progress-spinner",
    "off",
    ...dependencyFiles.flatMap((file) => ["-r", file]),
  ]);
}

if (roots.length === 0 || !roots.some(containsPythonFile)) {
  console.log(`Python ${mode} skipped: no Python sources exist yet.`);
  process.exit(0);
}

const pythonRoots = roots.filter(containsPythonFile);
const productPythonRoots = pythonRoots.filter((root) => root !== "tests");

if (mode === "typecheck") {
  if (productPythonRoots.length === 0) {
    console.log("Python typecheck skipped: no product Python sources exist yet.");
    process.exit(0);
  }
  run("uv", [
    "run",
    "--extra",
    "test",
    "mypy",
    "--config-file",
    "pyproject.toml",
    ...productPythonRoots,
  ]);
}

if (productPythonRoots.length === 0) {
  console.log("Python security skipped: no product Python sources exist yet.");
  process.exit(0);
}

run("bandit", ["--configfile", "pyproject.toml", "-r", ...productPythonRoots]);

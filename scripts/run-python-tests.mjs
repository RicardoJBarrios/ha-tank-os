import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

function containsPythonFile(path) {
  return readdirSync(path).some((entry) => {
    const child = join(path, entry);
    const stats = statSync(child);
    return stats.isDirectory() ? containsPythonFile(child) : child.endsWith(".py");
  });
}

if (!existsSync("tests") || !containsPythonFile("tests")) {
  console.log("Python tests skipped: no repository test files exist yet.");
  process.exit(0);
}

const args = ["run", "--locked", "--extra", "test", "pytest"];
if (process.platform === "win32") {
  // The HA plugin imports POSIX-only fcntl before pytest can collect tests.
  args.push("-p", "no:homeassistant");
  console.log(
    "Windows: Home Assistant pytest plugin disabled; runtime tests must report explicit skips. " +
      "Portable tests still run; Linux and macOS CI run the Home Assistant tests.",
  );
}

const result = spawnSync("uv", args, {
  stdio: "inherit",
  shell: false,
});

if (result.error) {
  console.error(`Unable to run pytest through uv: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);

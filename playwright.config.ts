import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.HA_TEST_URL ?? "http://127.0.0.1:8123";
const isCI = Boolean(process.env.CI);

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? 1 : undefined,
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  reporter: [
    ["list"],
    ["html", { outputFolder: "artifacts/playwright/report", open: "never" }],
    ["junit", { outputFile: "artifacts/playwright/junit.xml" }],
  ],
  outputDir: "artifacts/playwright/test-results",
  use: {
    baseURL,
    browserName: "chromium",
    ...devices["Desktop Chrome"],
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
    actionTimeout: 10_000,
  },
});

const url = process.env.HA_TEST_URL ?? "http://127.0.0.1:8123";
const timeoutMs = Number(process.env.HA_WAIT_TIMEOUT_MS ?? 120000);
const intervalMs = 2000;
const deadline = Date.now() + timeoutMs;

while (Date.now() < deadline) {
  try {
    const response = await fetch(`${url}/api/`);
    if (response.status === 401 || response.ok) {
      console.log(`Home Assistant is ready at ${url}.`);
      process.exit(0);
    }
  } catch {
    // The container may still be starting.
  }
  await new Promise((resolve) => setTimeout(resolve, intervalMs));
}

console.error(`Timed out waiting for Home Assistant at ${url}.`);
process.exit(1);

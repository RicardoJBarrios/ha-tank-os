const url = process.env.HA_TEST_URL ?? "http://127.0.0.1:8123";

try {
  const response = await fetch(`${url}/api/`);
  const body = await response.text();
  if (response.status === 401) {
    console.log(`Home Assistant is ready at ${url} (authentication required).`);
    process.exit(0);
  }

  console.error(`Home Assistant responded with HTTP ${response.status}: ${body}`);
  process.exit(1);
} catch (error) {
  console.error(`Home Assistant is not reachable at ${url}: ${error.message}`);
  process.exit(1);
}

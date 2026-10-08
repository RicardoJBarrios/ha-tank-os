const baseUrl = process.env.SONAR_HOST_URL ?? "http://127.0.0.1:9000";

const response = await fetch(`${baseUrl}/api/system/status`);
if (!response.ok) {
  console.error(`SonarQube status endpoint responded with HTTP ${response.status}.`);
  process.exit(1);
}

const payload = await response.json();
if (payload.status !== "UP") {
  console.error(`SonarQube is not ready: ${payload.status ?? "unknown"}.`);
  process.exit(1);
}

console.log(`SonarQube is ready at ${baseUrl} (${payload.version ?? "version unknown"}).`);

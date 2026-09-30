const url = process.env.HA_MCP_URL ?? "http://127.0.0.1:8123/api/mcp/assist";
const token = process.env.HA_TEST_TOKEN;

if (!token) {
  console.error("HA_TEST_TOKEN is not available in the current environment.");
  process.exit(2);
}

const response = await fetch(url, {
  method: "POST",
  headers: {
    Accept: "application/json, text/event-stream",
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: "ha-tank-os-status", version: "0.0.0" },
    },
  }),
});

if (!response.ok) {
  console.error(`Home Assistant MCP responded with HTTP ${response.status}.`);
  process.exit(1);
}

const payload = await response.json();
const server = payload.result?.serverInfo;
if (!server?.name || !server?.version) {
  console.error("Home Assistant MCP returned an invalid initialize response.");
  process.exit(1);
}

console.log(`Home Assistant MCP is ready: ${server.name} ${server.version} at ${url}.`);

/* eslint-disable no-console */
const fs = require('fs');
const path = require('path');
const http = require('http');
const url = require('url');
const { filterLanguages } = require('./common');

const destinationsDir = path.join(__dirname, '../src/configurations/destinations');

const getJSDeviceModeDestinations = () =>
  fs
    .readdirSync(destinationsDir)
    .map((destination) => {
      const dbConfig = fs.readFileSync(
        path.join(destinationsDir, destination, 'db-config.json'),
        'utf8',
      );
      return JSON.parse(dbConfig);
    })
    .filter((destination) => filterLanguages(destination, 'js'))
    .map((destinationDefinition) => {
      const cleanDestName = destinationDefinition.name.replace(/[^\dA-Za-z]/g, '');
      return {
        id: cleanDestName,
        name: destinationDefinition.name,
        config: {},
        enabled: true,
        destinationDefinitionId: cleanDestName,
        destinationDefinition: {
          name: destinationDefinition.name,
          displayName: destinationDefinition.displayName,
        },
        updatedAt: new Date().toISOString(),
      };
    });

const deviceModeJSDestinations = getJSDeviceModeDestinations();

// Sample JSON response for /sourceConfig
const getSourceConfig = (writeKey) => ({
  source: {
    id: 'someSourceId',
    name: 'http dev',
    writeKey,
    config: {
      statsCollection: {
        errors: {
          enabled: false,
        },
        metrics: {
          enabled: false,
        },
      },
    },
    enabled: true,
    workspaceId: 'someWorkspaceId',
    destinations: deviceModeJSDestinations,
    updatedAt: new Date().toISOString(),
    dataplanes: {},
  },
  updatedAt: new Date().toISOString(),
});

// Function to decode and validate Basic Auth
function getAuthInfo(authHeader) {
  if (!authHeader || !authHeader.startsWith('Basic ')) {
    return {};
  }

  // Decode the Base64 string
  const base64Credentials = authHeader.split(' ')[1];
  const credentials = Buffer.from(base64Credentials, 'base64').toString('utf-8');
  const [username, password] = credentials.split(':');

  return { username, password };
}

// Function to handle CORS
function setCorsHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*'); // Allow all origins
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'); // Allowed methods
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization'); // Allowed headers
}

// Create the HTTP server
const server = http.createServer((req, res) => {
  // Set CORS headers
  setCorsHeaders(res);

  // Handle OPTIONS preflight requests for CORS
  if (req.method === 'OPTIONS') {
    res.writeHead(204); // No Content
    res.end();
    return;
  }

  // Parse the request URL
  const parsedUrl = url.parse(req.url, true); // `true` parses query parameters into an object
  const { query } = parsedUrl;

  const authHeader = req.headers.authorization;

  const authInfo = getAuthInfo(authHeader);
  const writeKey = authInfo?.username || query.writeKey;

  // Set response headers
  res.writeHead(200, { 'Content-Type': 'application/json' });

  // Send JSON response
  res.end(JSON.stringify(getSourceConfig(writeKey)));
});

// Start the server
const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

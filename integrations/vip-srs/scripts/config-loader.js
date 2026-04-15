/**
 * VIP SRS Config Loader
 *
 * Loads customer config JSON and applies CLI overrides.
 * Used by e2e-sandbox-runner.js, verify-load.js, and purge-vip-data.sh.
 *
 * Config resolution order (last wins):
 *   1. Hardcoded defaults (fallback)
 *   2. Customer JSON config file
 *   3. CLI arguments (always win)
 *
 * Usage:
 *   var loadConfig = require('./config-loader');
 *   var config = loadConfig(process.argv.slice(2));
 *   // config.targetOrg, config.distId, config.apiVersion, etc.
 */

var fs = require('fs');
var path = require('path');

var DEFAULTS = {
  targetOrg: 'shipyard-ros2-sandbox',
  distId: '',
  apiVersion: 'v62.0',
  batchSize: 25,
  customer: '',
  supplierCode: ''
};

var DEFAULT_CONFIG_PATH = path.join(__dirname, '..', 'config', 'shipyard.json');

function loadConfig(cliArgs) {
  // 1. Start with hardcoded defaults
  var config = {};
  Object.keys(DEFAULTS).forEach(function(k) { config[k] = DEFAULTS[k]; });

  // 2. Find --config in CLI args (don't consume it — let caller parse other args)
  var configPath = DEFAULT_CONFIG_PATH;
  for (var i = 0; i < cliArgs.length; i++) {
    if (cliArgs[i] === '--config' && cliArgs[i + 1]) {
      configPath = cliArgs[i + 1];
      // Resolve relative paths from cwd
      if (!path.isAbsolute(configPath)) {
        configPath = path.resolve(process.cwd(), configPath);
      }
      break;
    }
  }

  // 3. Load JSON config
  if (fs.existsSync(configPath)) {
    try {
      var json = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (json.salesforce && json.salesforce.orgAlias) config.targetOrg = json.salesforce.orgAlias;
      if (json.salesforce && json.salesforce.apiVersion) config.apiVersion = json.salesforce.apiVersion;
      if (json.salesforce && json.salesforce.batchSize) config.batchSize = json.salesforce.batchSize;
      if (json.targetDistributorId) config.distId = json.targetDistributorId;
      if (json.customer) config.customer = json.customer;
      if (json.supplierCode) config.supplierCode = json.supplierCode;
      if (json.supplier) config.supplier = json.supplier;
      if (json.sftpPath) config.sftpPath = json.sftpPath;
      config._configFile = configPath;
    } catch (e) {
      console.error('WARNING: Failed to parse config ' + configPath + ': ' + e.message);
    }
  } else if (configPath !== DEFAULT_CONFIG_PATH) {
    // Only warn if user explicitly passed --config and the file doesn't exist
    console.error('ERROR: Config file not found: ' + configPath);
    process.exit(1);
  }

  // 4. CLI args override (caller handles this — we just provide the base config)
  return config;
}

module.exports = loadConfig;

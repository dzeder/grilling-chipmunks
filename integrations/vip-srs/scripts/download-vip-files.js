#!/usr/bin/env node
/**
 * VIP SRS SFTP File Downloader
 *
 * Downloads VIP data files from SFTP server, decompresses .gz files,
 * and saves as CSV ready for the e2e-sandbox-runner.
 *
 * Usage:
 *   node download-vip-files.js                      # download latest files
 *   node download-vip-files.js --list               # list available files on SFTP
 *   node download-vip-files.js --date 04082026      # specific file date (MMDDYYYY)
 *   node download-vip-files.js --file-type SLSDA    # single file type only
 *   node download-vip-files.js --config config/gulf.json  # different customer
 *   node download-vip-files.js --out-dir data/custom/     # custom output directory
 *
 * Prerequisites:
 *   npm install  (installs ssh2-sftp-client, dotenv)
 *   cp .env.example .env  (fill in SFTP credentials)
 */

var path = require('path');
var fs = require('fs');
var zlib = require('zlib');

// Load .env from integration root (one level up from scripts/)
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

var loadConfig = require('./config-loader');

// =============================================================================
// CONFIG
// =============================================================================

var VIP_FILE_TYPES = [
  'SRSCHAIN',
  'ITM2DA',
  'DISTDA',
  'ITMDA',
  'OUTDA',
  'INVDA',
  'SLSDA',
  'CTLDA'
];

// CLI args
var args = process.argv.slice(2);
var LIST_MODE = false;
var TARGET_DATE = ''; // MMDDYYYY format
var TARGET_TYPE = ''; // single file type filter
var OUT_DIR = '';      // custom output directory

for (var i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--list': LIST_MODE = true; break;
    case '--date':
      TARGET_DATE = args[++i] || '';
      // Accept YYYY-MM-DD, YYYYMMDD, or MMDDYYYY — normalize to YYYYMMDD
      TARGET_DATE = TARGET_DATE.replace(/-/g, '');
      if (TARGET_DATE.length === 8 && parseInt(TARGET_DATE.substring(0, 2), 10) <= 12) {
        // Looks like MMDDYYYY — convert to YYYYMMDD
        TARGET_DATE = TARGET_DATE.substring(4, 8) + TARGET_DATE.substring(0, 4);
      }
      break;
    case '--file-type': TARGET_TYPE = (args[++i] || '').toUpperCase(); break;
    case '--out-dir': OUT_DIR = args[++i]; break;
    case '--config': i++; break; // consumed by config-loader
    case '--help': case '-h':
      console.log('Usage: node download-vip-files.js [--list] [--date MMDDYYYY] [--file-type TYPE] [--config FILE] [--out-dir DIR]');
      console.log('');
      console.log('File types: ' + VIP_FILE_TYPES.join(', '));
      process.exit(0);
  }
}

// Load customer config for SFTP path
var cfg = loadConfig(args);
var SFTP_HOST = (process.env.VIP_SFTP_HOST || '').replace(/^https?:\/\//, '').replace(/\/+$/, '');
var SFTP_PORT = parseInt(process.env.VIP_SFTP_PORT || '22', 10);
var SFTP_USER = process.env.VIP_SFTP_USERNAME;
var SFTP_PASS = process.env.VIP_SFTP_PASSWORD;

if (!SFTP_HOST || !SFTP_USER || !SFTP_PASS) {
  console.error('ERROR: SFTP credentials not configured.');
  console.error('Copy .env.example to .env and fill in VIP_SFTP_HOST, VIP_SFTP_USERNAME, VIP_SFTP_PASSWORD');
  process.exit(1);
}

// SFTP base path: /vip/{SupplierCode}/ (e.g., /vip/ARG/)
var SFTP_BASE_PATH = cfg.sftpPath || ('/vip/' + (cfg.supplierCode || 'ARG') + '/');

// Filter file types if specified
var fileTypes = TARGET_TYPE
  ? VIP_FILE_TYPES.filter(function(t) { return t === TARGET_TYPE; })
  : VIP_FILE_TYPES;

if (TARGET_TYPE && fileTypes.length === 0) {
  console.error('ERROR: Unknown file type: ' + TARGET_TYPE);
  console.error('Valid types: ' + VIP_FILE_TYPES.join(', '));
  process.exit(1);
}

// =============================================================================
// SFTP OPERATIONS
// =============================================================================

async function main() {
  var SftpClient = require('ssh2-sftp-client');
  var sftp = new SftpClient();

  console.log('============================================');
  console.log('VIP SRS SFTP File Downloader');
  console.log('============================================');
  console.log('Host:        ' + SFTP_HOST + ':' + SFTP_PORT);
  console.log('User:        ' + SFTP_USER);
  console.log('Base path:   ' + SFTP_BASE_PATH);
  console.log('File types:  ' + fileTypes.join(', '));
  if (TARGET_DATE) console.log('Target date: ' + TARGET_DATE);
  console.log('Mode:        ' + (LIST_MODE ? 'LIST' : 'DOWNLOAD'));
  console.log('============================================');
  console.log('');

  try {
    console.log('Connecting to SFTP...');
    await sftp.connect({
      host: SFTP_HOST,
      port: SFTP_PORT,
      username: SFTP_USER,
      password: SFTP_PASS,
      readyTimeout: 10000,
      retries: 2,
      retry_minTimeout: 2000
    });
    console.log('Connected.');
    console.log('');

    // List files in base path
    var allFiles;
    try {
      allFiles = await sftp.list(SFTP_BASE_PATH);
    } catch (listErr) {
      console.error('ERROR listing ' + SFTP_BASE_PATH + ': ' + listErr.message);
      console.error('');
      console.error('Check that the SFTP path is correct. Try listing the root:');
      try {
        var rootFiles = await sftp.list('/');
        console.error('Root contents:');
        rootFiles.forEach(function(f) {
          console.error('  ' + (f.type === 'd' ? '[DIR] ' : '      ') + f.name);
        });
      } catch (_) { /* ignore */ }
      await sftp.end();
      process.exit(1);
    }

    // Filter to VIP data files (match TYPE*.N*.gz or TYPE*.csv patterns)
    var vipFiles = allFiles.filter(function(f) {
      if (f.type === 'd') return false; // skip directories
      var name = f.name.toUpperCase();
      return fileTypes.some(function(type) {
        return name.indexOf(type) === 0;
      });
    });

    // Sort by modification time (newest first)
    vipFiles.sort(function(a, b) { return b.modifyTime - a.modifyTime; });

    if (LIST_MODE) {
      console.log('Available files in ' + SFTP_BASE_PATH + ':');
      console.log('');
      if (vipFiles.length === 0) {
        console.log('  (no matching files found)');
        // Show all files for debugging
        if (allFiles.length > 0) {
          console.log('');
          console.log('All files in directory:');
          allFiles.forEach(function(f) {
            var sizeKb = Math.round(f.size / 1024);
            var date = new Date(f.modifyTime).toISOString().substring(0, 10);
            console.log('  ' + f.name + ' (' + sizeKb + ' KB, ' + date + ')');
          });
        }
      } else {
        // Group by file type
        var byType = {};
        vipFiles.forEach(function(f) {
          var type = f.name.split('.')[0].replace(/DA$|WK$|MN$/, function(m) { return m; }).toUpperCase();
          // Extract the file type prefix
          for (var ti = 0; ti < VIP_FILE_TYPES.length; ti++) {
            if (f.name.toUpperCase().indexOf(VIP_FILE_TYPES[ti]) === 0) {
              type = VIP_FILE_TYPES[ti];
              break;
            }
          }
          if (!byType[type]) byType[type] = [];
          byType[type].push(f);
        });

        Object.keys(byType).sort().forEach(function(type) {
          console.log('  ' + type + ':');
          byType[type].forEach(function(f) {
            var sizeKb = Math.round(f.size / 1024);
            var date = new Date(f.modifyTime).toISOString().substring(0, 10);
            console.log('    ' + f.name + ' (' + sizeKb + ' KB, modified ' + date + ')');
          });
        });
        console.log('');
        console.log('Total: ' + vipFiles.length + ' files');
      }

      await sftp.end();
      return;
    }

    // DOWNLOAD MODE — find the right files to download

    // If a specific date was requested, filter to that date
    var filesToDownload;
    if (TARGET_DATE) {
      filesToDownload = vipFiles.filter(function(f) {
        return f.name.indexOf('N' + TARGET_DATE) > -1;
      });
      if (filesToDownload.length === 0) {
        console.log('No files found for date ' + TARGET_DATE);
        console.log('Available dates:');
        var dates = {};
        vipFiles.forEach(function(f) {
          var match = f.name.match(/N(\d{8})/);
          if (match) dates[match[1]] = true;
        });
        Object.keys(dates).sort().reverse().forEach(function(d) {
          console.log('  ' + d);
        });
        await sftp.end();
        process.exit(1);
      }
    } else {
      // Download the latest file for each type
      filesToDownload = [];
      fileTypes.forEach(function(type) {
        var typeFiles = vipFiles.filter(function(f) {
          return f.name.toUpperCase().indexOf(type) === 0;
        });
        if (typeFiles.length > 0) {
          filesToDownload.push(typeFiles[0]); // newest first (already sorted)
        } else {
          console.log('WARNING: No files found for type ' + type);
        }
      });
    }

    if (filesToDownload.length === 0) {
      console.log('No files to download.');
      await sftp.end();
      return;
    }

    // Determine output directory
    // Extract date from first file for directory naming
    var dateMatch = filesToDownload[0].name.match(/N(\d{8})/);
    var fileDateStr = dateMatch ? dateMatch[1] : new Date().toISOString().replace(/-/g, '').substring(0, 8);
    // Convert YYYYMMDD to YYYY-MM-DD for directory name
    var dirDate = fileDateStr.length === 8
      ? fileDateStr.substring(0, 4) + '-' + fileDateStr.substring(4, 6) + '-' + fileDateStr.substring(6, 8)
      : fileDateStr;

    var outDir = OUT_DIR
      ? path.resolve(path.join(__dirname, '..'), OUT_DIR)
      : path.join(__dirname, '..', 'data', dirDate);

    // Create output directory
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }

    console.log('Downloading ' + filesToDownload.length + ' files to ' + outDir);
    console.log('');

    var downloaded = 0;
    var failed = 0;

    for (var fi = 0; fi < filesToDownload.length; fi++) {
      var file = filesToDownload[fi];
      var remotePath = SFTP_BASE_PATH + file.name;
      var isGzipped = file.name.toLowerCase().endsWith('.gz');

      // Determine output filename: strip .gz, normalize to TYPE.csv
      var outName = file.name;
      if (isGzipped) outName = outName.replace(/\.gz$/i, '');
      // Ensure .csv extension
      if (!outName.toLowerCase().endsWith('.csv')) {
        // VIP files may not have .csv extension — extract type and add it
        var typePrefix = '';
        for (var ti = 0; ti < VIP_FILE_TYPES.length; ti++) {
          if (outName.toUpperCase().indexOf(VIP_FILE_TYPES[ti]) === 0) {
            typePrefix = VIP_FILE_TYPES[ti];
            break;
          }
        }
        outName = typePrefix + '.csv';
      }

      var outPath = path.join(outDir, outName);
      var sizeKb = Math.round(file.size / 1024);

      process.stdout.write('  [' + (fi + 1) + '/' + filesToDownload.length + '] ' + file.name + ' (' + sizeKb + ' KB)...');

      try {
        if (isGzipped) {
          // Download to buffer, then decompress
          var buffer = await sftp.get(remotePath);
          var decompressed = zlib.gunzipSync(buffer);
          fs.writeFileSync(outPath, decompressed);
          var decompKb = Math.round(decompressed.length / 1024);
          console.log(' OK (' + decompKb + ' KB decompressed) → ' + outName);
        } else {
          // Download directly
          await sftp.fastGet(remotePath, outPath);
          console.log(' OK → ' + outName);
        }
        downloaded++;
      } catch (dlErr) {
        console.log(' FAILED: ' + dlErr.message);
        failed++;
      }
    }

    console.log('');
    console.log('============================================');
    console.log('Downloaded: ' + downloaded + ' files');
    if (failed > 0) console.log('Failed:     ' + failed + ' files');
    console.log('Output dir: ' + outDir);
    console.log('============================================');
    console.log('');
    console.log('Next steps:');
    console.log('  # Dry run (no API calls):');
    console.log('  node scripts/e2e-sandbox-runner.js --data-dir ' + path.relative(path.join(__dirname, '..'), outDir) + '/ --dry-run');
    console.log('');
    console.log('  # Live load:');
    console.log('  node scripts/e2e-sandbox-runner.js --data-dir ' + path.relative(path.join(__dirname, '..'), outDir) + '/');

    await sftp.end();
  } catch (err) {
    console.error('');
    console.error('FATAL: ' + err.message);
    if (err.code === 'ECONNREFUSED') {
      console.error('Connection refused. Check VIP_SFTP_HOST and VIP_SFTP_PORT in .env');
    } else if (err.message.indexOf('Authentication') > -1 || err.message.indexOf('auth') > -1) {
      console.error('Authentication failed. Check VIP_SFTP_USERNAME and VIP_SFTP_PASSWORD in .env');
    } else if (err.message.indexOf('getaddrinfo') > -1) {
      console.error('DNS resolution failed. Check VIP_SFTP_HOST in .env');
    }
    try { await sftp.end(); } catch (_) { /* ignore */ }
    process.exit(1);
  }
}

main();

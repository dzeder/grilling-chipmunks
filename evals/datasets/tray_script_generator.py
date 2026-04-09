"""Eval dataset for the tray-script-generator skill.

Each case is a script generation request with a pre-recorded output.
Cases cover structure compliance, FP patterns, library usage, SF-specific rules,
and error handling — matching the 6-point quality checklist from the SKILL.md.

Two categories of cases:
  - tag "passing" — well-formed scripts that should pass all checks (4 cases)
  - tag "violation" — intentionally flawed scripts to verify scorer detection (5 cases)

CI usage:
  python3 evals/run_evals.py --agent tray_script_generator --tag passing
  python3 evals/run_evals.py --agent tray_script_generator --tag violation  # expect 0% (scorer verification)
"""

EVAL_CASES = [
    # --- Passing cases ---
    {
        "name": "basic_sf_composite_upsert",
        "description": "Generate a script that builds SF composite upsert requests for product data",
        "tags": ["basic", "salesforce", "composite", "passing"],
        "input": {
            "prompt": "Generate a Tray script that takes product data and builds Salesforce composite upsert requests with external IDs",
            "context": "Ohanafy product sync, namespace ohfy__",
        },
        "expected": {
            "requires_url_encoding": True,
            "requires_error_handling": True,
        },
        "recorded_output": {
            "script": """
const CONFIG = {
    SALESFORCE_API_VERSION: 'v62.0',
    BATCH_SIZE: 200,
    NAMESPACE: 'ohfy__'
};

exports.step = function({data = [], configuration = {}}, fileInput) {
    const validated = validateInput(data);
    const requests = buildCompositeRequests(validated, configuration);
    return formatOutput(requests);
};

function validateInput(data) {
    if (!Array.isArray(data)) {
        return { error: { message: 'Input data must be an array', statusCode: 400, retryable: false } };
    }
    return data.filter(function(item) { return item && item.product_id; });
}

function buildCompositeRequests(items, config) {
    var namespace = config.namespace_prefix || CONFIG.NAMESPACE;
    return items.map(function(item, index) {
        var externalId = buildExternalId('product', item.product_id);
        var encodedId = encodeURIComponent(externalId);
        var url = '/services/data/' + CONFIG.SALESFORCE_API_VERSION + '/sobjects/Product2/' + buildFieldName('External_ID__c', namespace) + '/' + encodedId;
        return {
            method: 'PATCH',
            url: url,
            referenceId: 'product_' + index,
            body: {
                Name: item.name,
                ProductCode: item.sku,
                IsActive: true
            }
        };
    });
}

function buildExternalId(service, id) {
    return service + '_' + id;
}

function buildFieldName(baseName, namespace_prefix) {
    return namespace_prefix ? namespace_prefix + baseName : baseName;
}

function formatOutput(requests) {
    return {
        compositeRequest: requests,
        totalRecords: requests.length,
        batchSize: CONFIG.BATCH_SIZE
    };
}
""",
            "patterns_used": ["composite_request_builder", "url_encoding", "namespace_handling"],
        },
    },
    {
        "name": "lookup_map_transform",
        "description": "Generate a script that transforms data using lookup maps",
        "tags": ["basic", "data-processing", "lookup-map", "passing"],
        "input": {
            "prompt": "Generate a Tray script that transforms inventory records using lookup maps for status codes",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const STATUS_MAP = {
    'A': 'Active',
    'I': 'Inactive',
    'D': 'Discontinued',
    'P': 'Pending'
};

const CATEGORY_MAP = {
    'BEER': 'Beer',
    'WINE': 'Wine',
    'SPIRIT': 'Spirits',
    'NA': 'Non-Alcoholic'
};

exports.step = function({data = [], configuration = {}}, fileInput) {
    var validated = validateInput(data);
    var transformed = transformRecords(validated);
    return formatOutput(transformed);
};

function validateInput(data) {
    if (!Array.isArray(data)) {
        return [];
    }
    return data.filter(function(record) { return record && record.sku; });
}

function transformRecords(records) {
    return records.map(function(record) {
        return {
            sku: record.sku,
            name: record.product_name || 'Unknown',
            status: lookupValue(STATUS_MAP, record.status_code, 'Unknown'),
            category: lookupValue(CATEGORY_MAP, record.category_code, 'Other'),
            quantity: parseNumeric(record.qty_on_hand)
        };
    });
}

function lookupValue(map, key, defaultValue) {
    return map[key] || defaultValue;
}

function parseNumeric(value) {
    var parsed = Number(value);
    return isNaN(parsed) ? 0 : parsed;
}

function formatOutput(records) {
    return {
        records: records,
        count: records.length,
        timestamp: new Date().toISOString()
    };
}
""",
            "patterns_used": ["lookup_map", "filter_reduce_chain"],
        },
    },
    {
        "name": "statistics_aggregation",
        "description": "Generate a script that aggregates processing statistics for CSV output",
        "tags": ["basic", "statistics", "csv", "passing"],
        "input": {
            "prompt": "Generate a Tray script that computes summary statistics from batch processing results",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const RESULT_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    SKIPPED: 'skipped'
};

exports.step = function({data = [], configuration = {}}, fileInput) {
    var results = validateResults(data);
    var stats = computeStatistics(results);
    return formatStatistics(stats);
};

function validateResults(data) {
    if (!Array.isArray(data)) {
        return [];
    }
    return data.filter(function(r) { return r && r.status; });
}

function computeStatistics(results) {
    return results.reduce(function(acc, result) {
        var type = result.status || RESULT_TYPES.ERROR;
        return Object.assign({}, acc, {
            total: acc.total + 1,
            success: acc.success + (type === RESULT_TYPES.SUCCESS ? 1 : 0),
            errors: acc.errors + (type === RESULT_TYPES.ERROR ? 1 : 0),
            skipped: acc.skipped + (type === RESULT_TYPES.SKIPPED ? 1 : 0)
        });
    }, { total: 0, success: 0, errors: 0, skipped: 0 });
}

function formatStatistics(stats) {
    var successRate = stats.total > 0 ? (stats.success / stats.total * 100).toFixed(1) : '0.0';
    return {
        summary: {
            total_processed: stats.total,
            successful: stats.success,
            failed: stats.errors,
            skipped: stats.skipped,
            success_rate: successRate + '%'
        }
    };
}
""",
            "patterns_used": ["statistics_aggregation", "filter_reduce_chain"],
        },
    },
    {
        "name": "error_handling_complete",
        "description": "Generate a script with comprehensive error handling and retry strategies",
        "tags": ["error-handling", "advanced", "passing"],
        "input": {
            "prompt": "Generate a Tray script with full ERROR_TYPES enumeration and retry strategies for SF API calls",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": True,
        },
        "recorded_output": {
            "script": """
const ERROR_TYPES = {
    VALIDATION: 'ValidationFailed',
    AUTH: 'AuthenticationError',
    RATE_LIMIT: 'RateLimitExceeded',
    NOT_FOUND: 'RecordNotFound',
    DUPLICATE: 'DuplicateRecord',
    SERVER: 'ServerError'
};

const RETRY_CONFIG = {
    MAX_RETRIES: 3,
    BASE_DELAY_MS: 1000,
    BACKOFF_MULTIPLIER: 2
};

exports.step = function({data = [], configuration = {}}, fileInput) {
    var validated = validateInput(data);
    if (validated.error) {
        return validated;
    }
    var processed = processResults(validated);
    return formatOutput(processed);
};

function validateInput(data) {
    if (!Array.isArray(data)) {
        return buildError(ERROR_TYPES.VALIDATION, 'Input must be an array', 400, false);
    }
    if (data.length === 0) {
        return buildError(ERROR_TYPES.VALIDATION, 'Input array is empty', 400, false);
    }
    return data;
}

function processResults(results) {
    return results.map(function(result) {
        if (result.statusCode >= 500) {
            return Object.assign({}, result, {
                error: buildError(ERROR_TYPES.SERVER, result.message || 'Server error', result.statusCode, true),
                retryStrategy: buildRetryStrategy(true)
            });
        }
        if (result.statusCode === 429) {
            return Object.assign({}, result, {
                error: buildError(ERROR_TYPES.RATE_LIMIT, 'Rate limit exceeded', 429, true),
                retryStrategy: buildRetryStrategy(true)
            });
        }
        return result;
    });
}

function buildError(type, message, statusCode, retryable) {
    return {
        error: {
            response: { body: { Type: type, Message: message } },
            message: message,
            statusCode: statusCode,
            retryable: retryable,
            retryStrategy: buildRetryStrategy(retryable)
        }
    };
}

function buildRetryStrategy(retryable) {
    return {
        maxRetries: retryable ? RETRY_CONFIG.MAX_RETRIES : 0,
        delayMs: retryable ? RETRY_CONFIG.BASE_DELAY_MS : null,
        backoffMultiplier: RETRY_CONFIG.BACKOFF_MULTIPLIER,
        recommendation: retryable ? 'Retry with exponential backoff' : 'Not retryable, fix error and resubmit'
    };
}

function formatOutput(results) {
    var errors = results.filter(function(r) { return r.error; });
    return {
        results: results,
        errorCount: errors.length,
        hasRetryable: errors.some(function(e) { return e.error && e.error.retryable; })
    };
}
""",
            "patterns_used": ["error_types", "retry_strategy", "http_status_mapping"],
        },
    },
    # --- Failing cases (test that scorer catches violations) ---
    # These cases have expected_pass: False — the test runner inverts assertions.
    {
        "name": "violation_inline_functions",
        "description": "Script with inline function definitions inside exports.step — should fail fp_compliance",
        "tags": ["violation", "fp", "failing"],
        "expected_pass": False,
        "input": {
            "prompt": "Transform data",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const CONFIG = { VERSION: '1.0' };

exports.step = function({data = [], configuration = {}}, fileInput) {
    const transform = (item) => {
        return { name: item.name.toUpperCase() };
    };
    const validate = function(items) {
        return items.filter(function(i) { return i.name; });
    };
    return data.map(transform);
};
""",
            "patterns_used": [],
        },
    },
    {
        "name": "violation_console_log",
        "description": "Script with console.log statements — should fail fp_compliance",
        "tags": ["violation", "fp", "failing"],
        "expected_pass": False,
        "input": {
            "prompt": "Process records",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const CONFIG = { BATCH_SIZE: 100 };

exports.step = function({data = [], configuration = {}}, fileInput) {
    var processed = processData(data);
    return formatOutput(processed);
};

function processData(data) {
    console.log('Processing', data.length, 'records');
    return data.map(function(item) {
        console.log('Item:', item.id);
        return { id: item.id, name: item.name };
    });
}

function formatOutput(records) {
    return { records: records, count: records.length };
}
""",
            "patterns_used": [],
        },
    },
    {
        "name": "violation_unavailable_library",
        "description": "Script that imports axios — should fail library_compliance",
        "tags": ["violation", "library", "failing"],
        "expected_pass": False,
        "input": {
            "prompt": "Fetch and transform API data",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const axios = require('axios');
const cheerio = require('cheerio');

const CONFIG = { API_URL: 'https://api.example.com' };

exports.step = function({data = [], configuration = {}}, fileInput) {
    var results = transformData(data);
    return formatOutput(results);
};

function transformData(data) {
    return data.map(function(item) { return { id: item.id }; });
}

function formatOutput(results) {
    return { results: results };
}
""",
            "patterns_used": [],
        },
    },
    {
        "name": "violation_missing_url_encoding",
        "description": "SF composite script without encodeURIComponent — should fail sf_url_encoding",
        "tags": ["violation", "salesforce", "failing"],
        "expected_pass": False,
        "input": {
            "prompt": "Build SF composite upsert with external IDs",
        },
        "expected": {
            "requires_url_encoding": True,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const CONFIG = {
    SALESFORCE_API_VERSION: 'v62.0'
};

exports.step = function({data = [], configuration = {}}, fileInput) {
    var requests = buildRequests(data);
    return formatOutput(requests);
};

function buildRequests(items) {
    return items.map(function(item, index) {
        var url = '/services/data/' + CONFIG.SALESFORCE_API_VERSION + '/sobjects/Product2/External_ID__c/' + item.external_id;
        return {
            method: 'PATCH',
            url: url,
            referenceId: 'ref_' + index,
            body: { Name: item.name }
        };
    });
}

function formatOutput(requests) {
    return { compositeRequest: requests, count: requests.length };
}
""",
            "patterns_used": ["composite_request_builder"],
        },
    },
    {
        "name": "violation_imperative_loops",
        "description": "Script using for loops instead of .map/.filter/.reduce — should fail fp_compliance",
        "tags": ["violation", "fp", "failing"],
        "expected_pass": False,
        "input": {
            "prompt": "Transform product list",
        },
        "expected": {
            "requires_url_encoding": False,
            "requires_error_handling": False,
        },
        "recorded_output": {
            "script": """
const CONFIG = { MAX_ITEMS: 1000 };

exports.step = function({data = [], configuration = {}}, fileInput) {
    var processed = processItems(data);
    return formatOutput(processed);
};

function processItems(items) {
    var results = [];
    for (var i = 0; i < items.length; i++) {
        if (items[i].active) {
            results.push({ name: items[i].name, index: i });
        }
    }
    return results;
}

function formatOutput(items) {
    var total = 0;
    for (var j = 0; j < items.length; j++) {
        total = total + 1;
    }
    return { items: items, total: total };
}
""",
            "patterns_used": [],
        },
    },
]

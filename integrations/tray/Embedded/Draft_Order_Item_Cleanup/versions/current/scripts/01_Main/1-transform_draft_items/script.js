/**
 * Draft Order Item Cleanup — Transform Step
 *
 * Takes SOQL query results (from raw_http_request) and builds
 * batch_update_list payloads for Salesforce batch_update_records.
 *
 * Input: input.data = array of SF records (passed via script variables)
 * Output: array with single object containing batch_update_list
 *
 * Pattern: matches real Tray batch_update_records format:
 *   { object_id, fields: [{ key, value }] }
 */

exports.step = function(input, fileInput) {
    var records = input.data;

    var batchUpdateList = records.map(function(record) {
        return {
            object_id: record.Id,
            fields: [
                {
                    key: "ohfy__Is_Draft__c",
                    value: false
                }
            ]
        };
    });

    return [
        {
            object: "ohfy__Order_Item__c",
            error_handling: "rollback_fail",
            batch_update_list: batchUpdateList
        }
    ];
};

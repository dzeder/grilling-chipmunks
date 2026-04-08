exports.step = function(input, fileInput) {
  var records = input.records;
  var batchUpdateList = [];

  for (var i = 0; i < records.length; i++) {
    batchUpdateList.push({
      object_id: records[i].Id,
      fields: [
        { key: "ohfy__Is_Draft__c", value: false }
      ]
    });
  }

  return {
    batch_update_list: batchUpdateList,
    count: records.length,
    success_message: ":white_check_mark: *Draft Order Item Cleanup — SUCCESS*\n\nUpdated " + records.length + " draft order item(s) to non-draft."
  };
};

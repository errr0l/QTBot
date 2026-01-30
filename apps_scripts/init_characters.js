// 初始化表格【只执行一次】
// 创建谷歌表格后，将表格id设置到getSheetById方法中，并将角色json文件上传到谷歌硬盘，再执行initSheets
function initSheets() {
    const sheet = getSheetById();
    const characters = readJsonFromDrive("character_v5_2.json") || [];
    const fieldMappings = readJsonFromDrive("field_mappings.json") || {};
    const fields = [];
    const chinese_fields = [];
    for (const key in fieldMappings) {
        fields.push(key);
        chinese_fields.push(fieldMappings[key])
    }

    if (sheet.getRange("A1").getValue() === "") {
        sheet.getRange(1, 1, 1, chinese_fields.length).setValues([chinese_fields]);
    }
    const rows = [];
    for (const item of characters) {
        let row = [];
        for (const key of fields) {
            let value = item[key];
            if (value) {
                if (typeof value == 'string') {
                    value = value.trim();
                    if ((value.startsWith('{') && value.endsWith('}')) || (value.startsWith('[') && value.endsWith(']'))) {
                        const parsed = JSON.parse(value);
                        value = JSON.stringify(parsed, null, 2);
                    }
                }
                else if (typeof value == 'object') {
                    value = JSON.stringify(value, null, 2);
                }
            }
            row.push(value);
        }
        rows.push(row);
    }
    const lastRow = sheet.getLastRow();
    const startRow = lastRow + 1;
    if (rows.length) {
        sheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
        console.log(`成功写入${rows.length}行数据`);
    }
}

// 从硬盘中读取文件
function readJsonFromDrive(name) {
    const files = DriveApp.getFilesByName(name);
    if (files.hasNext()) {
        const file = files.next();
        const blob = file.getBlob();
        const content = blob.getDataAsString();
        return JSON.parse(content);
    }
    return null;
}

function getSheetById() {
    const ss = SpreadsheetApp.openById('谷歌表格id');
    return ss.getSheetByName("工作表1");
}
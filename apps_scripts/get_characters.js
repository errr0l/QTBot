function doGet(request = {}) {
    const properties = PropertiesService.getScriptProperties();

    const API_KEY = properties.getProperty("API_KEY");
    const apiKey = request.parameter?.apiKey;
    if (!apiKey || API_KEY !== apiKey) {
        return output({
            message: `秘钥不正确`,
            code: 400
        });
    }

    const sheetName = properties.getProperty("SHEET_NAME");
    const sheetId = properties.getProperty("SHEET_ID");
    const ss = SpreadsheetApp.openById(sheetId);
    const sheet = ss?.getSheetByName(sheetName);
    if (!sheet) {
        return output({
            message: `表格${sheetName}不存在`,
            code: 500
        });
    }
    const lastRow = sheet.getLastRow();
    const lastCol = sheet.getLastColumn();

    if (lastRow < 2) {
        return output({
            "rows": [],
            "message": "ok",
            "code": 200
        });
    }

    const range = sheet.getRange(1, 1, lastRow, lastCol);
    const values = range.getValues();

    const rows = values.slice(1);

    const fieldMappings = readJsonFromDrive("field_mappings.json");

    const fields = Object.keys(fieldMappings);
    const characters = [];
    for (const row of rows) {
        const character = {};
        for (let i=0; i<fields.length; i++) {
            let value = row[i];
            // 转为紧凑型json字符
            if (value && typeof value == 'string') {
                if ((value.startsWith('{') && value.endsWith('}')) || (value.startsWith('[') && value.endsWith(']'))) {
                    const parsed = JSON.parse(value);
                    value = JSON.stringify(parsed);
                }
            }
            character[fields[i]] = value;
        }
        characters.push(character);
    }

    return output({
        "rows": characters,
        "message": "ok",
        "code": 200
    });
}

// 返回json数据
function output(respData) {
    const output = ContentService.createTextOutput(JSON.stringify(respData));
    output.setMimeType(ContentService.MimeType.JSON);
    return output;
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
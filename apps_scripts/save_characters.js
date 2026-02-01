/**
 * 保存角色接口；
 * @param request
 * @returns {*}
 */
function doPost(request) {
    try {
        const payload = JSON.parse(request.postData.contents) || {};
        const { apiKey, data } = payload;
        if (!apiKey || !data) {
            return output({
                "message": "apiKey或角色数据不能为空",
                code: 400
            });
        }
        const properties = PropertiesService.getScriptProperties();

        const API_KEY = properties.getProperty("API_KEY");

        if (!API_KEY || API_KEY !== payload.apiKey) {
            throw new Error(`秘钥不正确`);
        }
        const sheetName = properties.getProperty("SHEET_NAME");
        const sheetId = properties.getProperty("SHEET_ID");
        const ss = SpreadsheetApp.openById(sheetId);
        const sheet = ss.getSheetByName(sheetName);
        if (!sheet) throw new Error(`表格${sheetName}不存在`);

        const characters = data;

        const fieldMappings = readJsonFromDrive("field_mappings.json");
        const fields = Object.keys(fieldMappings);
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
        if (rows.length) {
            const lastRow = sheet.getLastRow();
            const startRow = lastRow + 1;
            sheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
        }

        // 以code为主，调用方收到200表示插入成功
        return output({
            "message": `成功写入${rows.length}行数据`,
            "code": 200
        });

    }
    catch (err) {
        return output({
            message: err.message,
            code: 500
        });
    }
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

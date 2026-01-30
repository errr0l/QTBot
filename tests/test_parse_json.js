const fs = require("fs");

const characterJson = fs.readFileSync(__dirname + "/../data/main_character_v4.json", encoding="utf-8");

if (characterJson) {
    const characters = JSON.parse(characterJson);

    console.log(characters[0]);
}
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
exports.sendMoodMessage = exports.deleteMarkupKeyboard = exports.sendThatsItMessage = exports.sendHurryUpMessage = exports.sendMessageToUser = exports.sendMessageToAdmins = exports.getUserByTelegramId = exports.getTelegramId = void 0;
var mongodb_1 = require("../mongodb");
var tg_messages_1 = require("../../tg_messages");
var getTelegramId = function (userId) { return __awaiter(void 0, void 0, void 0, function () {
    var client, collection, user;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, mongodb_1["default"]];
            case 1:
                client = _a.sent();
                collection = client.db("roger-bot-db").collection("users");
                return [4 /*yield*/, collection.findOne({ "_id": userId }, {
                        'telegram_id': 1
                    })];
            case 2:
                user = _a.sent();
                return [2 /*return*/, user.telegram_id];
        }
    });
}); };
exports.getTelegramId = getTelegramId;
var getUserByTelegramId = function (telegramId) { return __awaiter(void 0, void 0, void 0, function () {
    var client, collection, user;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, mongodb_1["default"]];
            case 1:
                client = _a.sent();
                collection = client.db("roger-bot-db").collection("users");
                return [4 /*yield*/, collection.findOne({ "telegram_id": telegramId })];
            case 2:
                user = _a.sent();
                return [2 /*return*/, user];
        }
    });
}); };
exports.getUserByTelegramId = getUserByTelegramId;
var sendMessageToAdmins = function (message) { return __awaiter(void 0, void 0, void 0, function () {
    var client, collection, cursorUsers, adminUsers;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, mongodb_1["default"]];
            case 1:
                client = _a.sent();
                collection = client.db("roger-bot-db").collection("users");
                return [4 /*yield*/, collection.find({ "is_admin": true, "is_active": true }, {
                        '_id': 0, 'telegram_id': 1
                    })];
            case 2:
                cursorUsers = _a.sent();
                return [4 /*yield*/, cursorUsers.toArray()];
            case 3:
                adminUsers = _a.sent();
                return [4 /*yield*/, Promise.all(adminUsers.map(function (user) { return __awaiter(void 0, void 0, void 0, function () {
                        var e_1;
                        return __generator(this, function (_a) {
                            switch (_a.label) {
                                case 0:
                                    _a.trys.push([0, 3, , 4]);
                                    return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/sendMessage?chat_id=").concat(user.telegram_id, "&text=").concat(message), { method: 'POST' })];
                                case 1: return [4 /*yield*/, _a.sent()];
                                case 2:
                                    _a.sent();
                                    return [3 /*break*/, 4];
                                case 3:
                                    e_1 = _a.sent();
                                    console.log("Ошибка при отправке сообщения Админам: ", e_1);
                                    return [3 /*break*/, 4];
                                case 4: return [2 /*return*/];
                            }
                        });
                    }); }))];
            case 4:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); };
exports.sendMessageToAdmins = sendMessageToAdmins;
var sendMessageToUser = function (userTelegramId, message) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/sendMessage?chat_id=").concat(userTelegramId, "&text=").concat(message), { method: 'POST' })];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); };
exports.sendMessageToUser = sendMessageToUser;
var sendHurryUpMessage = function (userTelegramId) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/sendMessage?chat_id=").concat(userTelegramId, "&text=").concat((0, tg_messages_1.getHurryUpMessage)()), { method: 'POST' })];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); };
exports.sendHurryUpMessage = sendHurryUpMessage;
var sendThatsItMessage = function (userTelegramId) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/sendMessage?chat_id=").concat(userTelegramId, "&text=").concat((0, tg_messages_1.getThatsItMessage)()), { method: 'POST' })];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); };
exports.sendThatsItMessage = sendThatsItMessage;
var deleteMarkupKeyboard = function (userTelegramId, messageId) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/editMessageReplyMarkup?chat_id=").concat(userTelegramId, "&message_id=").concat(messageId, "&reply_markup=[]"), { method: 'POST' })];
            case 1: return [2 /*return*/, _a.sent()];
        }
    });
}); };
exports.deleteMarkupKeyboard = deleteMarkupKeyboard;
var sendMoodMessage = function (userTelegramId) { return __awaiter(void 0, void 0, void 0, function () {
    var user, client, mentalRateCl, options, prevMentalRate, buttons, resp, data;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, (0, exports.getUserByTelegramId)(userTelegramId)];
            case 1:
                user = _a.sent();
                return [4 /*yield*/, mongodb_1["default"]];
            case 2:
                client = _a.sent();
                mentalRateCl = client.db("roger-bot-db").collection("mental_rate");
                options = {
                    sort: { "date": -1 },
                    projection: { id_tg_message: 1 }
                };
                return [4 /*yield*/, mentalRateCl.findOne({ "rate": 0, "id_user": user['_id'] }, options)];
            case 3:
                prevMentalRate = _a.sent();
                if (!prevMentalRate) return [3 /*break*/, 5];
                return [4 /*yield*/, (0, exports.deleteMarkupKeyboard)(userTelegramId, prevMentalRate.id_tg_message)];
            case 4:
                _a.sent();
                _a.label = 5;
            case 5:
                buttons = {
                    inline_keyboard: [[{
                                text: '🟢',
                                callback_data: 'green_button_answer'
                            },
                            {
                                text: '🟡',
                                callback_data: 'yellow_button_answer'
                            },
                            {
                                text: '🟠',
                                callback_data: 'orange_button_answer'
                            },
                            {
                                text: '🔴',
                                callback_data: 'red_button_answer'
                            }]]
                };
                return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/sendMessage?chat_id=").concat(userTelegramId, "&text=").concat((0, tg_messages_1.getGreetingsMessage)(), "&parse_mode=Markdown"), { method: 'POST' })];
            case 6:
                _a.sent();
                return [4 /*yield*/, fetch("https://api.telegram.org/bot".concat(process.env.ROGER_TOKEN_BOT, "/sendMessage?chat_id=").concat(userTelegramId, "&text=").concat((0, tg_messages_1.getMoodMessage)(), "&parse_mode=Markdown&reply_markup=").concat(JSON.stringify(buttons)), { method: 'POST' })];
            case 7:
                resp = _a.sent();
                return [4 /*yield*/, resp.json()];
            case 8:
                data = _a.sent();
                return [2 /*return*/, data.result];
        }
    });
}); };
exports.sendMoodMessage = sendMoodMessage;

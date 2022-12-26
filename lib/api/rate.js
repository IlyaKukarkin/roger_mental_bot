"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
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
var __asyncValues = (this && this.__asyncValues) || function (o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
};
exports.__esModule = true;
exports.getCalculatedRates = void 0;
var mongodb_1 = require("../mongodb");
var users_1 = require("./users");
var getCalculatedRates = function () { return __awaiter(void 0, void 0, void 0, function () {
    var client, messagesCol, settingsCol, usersCol, messages, settings, updateToApproved, updateToReview, _a, messages_1, messages_1_1, message, calculatedMessage, user, e_1_1, filterToApproved, filterToReview, docToApproved, docToReview, resultApprove, resString, resString, resultReview, resString, resString;
    var _b, e_1, _c, _d;
    return __generator(this, function (_e) {
        switch (_e.label) {
            case 0: return [4 /*yield*/, mongodb_1["default"]];
            case 1:
                client = _e.sent();
                messagesCol = client.db("roger-bot-db").collection("messages");
                settingsCol = client.db("roger-bot-db").collection("app_settings");
                usersCol = client.db("roger-bot-db").collection("users");
                return [4 /*yield*/, messagesCol.aggregate([
                        {
                            '$lookup': {
                                'from': 'rate',
                                'localField': '_id',
                                'foreignField': 'id_message',
                                'pipeline': [
                                    {
                                        '$lookup': {
                                            'from': 'users',
                                            'localField': 'id_user',
                                            'foreignField': '_id',
                                            'as': 'user'
                                        }
                                    }, {
                                        '$addFields': {
                                            'user': {
                                                '$first': '$user'
                                            }
                                        }
                                    }
                                ],
                                'as': 'rates'
                            }
                        }, {
                            '$addFields': {
                                'admin_good_rates': {
                                    '$filter': {
                                        'input': '$rates',
                                        'cond': {
                                            '$and': [
                                                {
                                                    '$eq': [
                                                        '$$item.user.is_admin', true
                                                    ]
                                                }, {
                                                    '$eq': [
                                                        '$$item.rate', true
                                                    ]
                                                }
                                            ]
                                        },
                                        'as': 'item'
                                    }
                                },
                                'admin_bad_rates': {
                                    '$filter': {
                                        'input': '$rates',
                                        'cond': {
                                            '$and': [
                                                {
                                                    '$eq': [
                                                        '$$item.user.is_admin', true
                                                    ]
                                                }, {
                                                    '$eq': [
                                                        '$$item.rate', false
                                                    ]
                                                }
                                            ]
                                        },
                                        'as': 'item'
                                    }
                                },
                                'user_good_rates': {
                                    '$filter': {
                                        'input': '$rates',
                                        'cond': {
                                            '$and': [
                                                {
                                                    '$eq': [
                                                        '$$item.user.is_admin', false
                                                    ]
                                                }, {
                                                    '$eq': [
                                                        '$$item.rate', true
                                                    ]
                                                }
                                            ]
                                        },
                                        'as': 'item'
                                    }
                                },
                                'user_bad_rates': {
                                    '$filter': {
                                        'input': '$rates',
                                        'cond': {
                                            '$and': [
                                                {
                                                    '$eq': [
                                                        '$$item.user.is_admin', false
                                                    ]
                                                }, {
                                                    '$eq': [
                                                        '$$item.rate', false
                                                    ]
                                                }
                                            ]
                                        },
                                        'as': 'item'
                                    }
                                }
                            }
                        }, {
                            '$addFields': {
                                'admin_good_rates': {
                                    '$size': '$admin_good_rates'
                                },
                                'admin_bad_rates': {
                                    '$size': '$admin_bad_rates'
                                },
                                'user_good_rates': {
                                    '$size': '$user_good_rates'
                                },
                                'user_bad_rates': {
                                    '$size': '$user_bad_rates'
                                }
                            }
                        }
                    ])];
            case 2:
                messages = _e.sent();
                return [4 /*yield*/, settingsCol.findOne()];
            case 3:
                settings = _e.sent();
                updateToApproved = [];
                updateToReview = [];
                //потом убрать
                return [4 /*yield*/, (0, users_1.sendMessageToAdmins)("Сорри, тут тестово выведу, кому бы написал бот, что его сообщение прошло модерацию 😘")];
            case 4:
                //потом убрать
                _e.sent();
                _e.label = 5;
            case 5:
                _e.trys.push([5, 16, 17, 22]);
                _a = true, messages_1 = __asyncValues(messages);
                _e.label = 6;
            case 6: return [4 /*yield*/, messages_1.next()];
            case 7:
                if (!(messages_1_1 = _e.sent(), _b = messages_1_1.done, !_b)) return [3 /*break*/, 15];
                _d = messages_1_1.value;
                _a = false;
                _e.label = 8;
            case 8:
                _e.trys.push([8, , 13, 14]);
                message = _d;
                calculatedMessage = calculateRate(message, settings);
                if (!(message.is_approved !== calculatedMessage.is_approved)) return [3 /*break*/, 12];
                if (!calculatedMessage.is_approved) return [3 /*break*/, 11];
                updateToApproved.push(calculatedMessage._id);
                return [4 /*yield*/, usersCol.findOne([
                        {
                            '$match': {
                                '_id': message.id_user
                            }
                        }
                    ])];
            case 9:
                user = _e.sent();
                return [4 /*yield*/, (0, users_1.sendMessageToAdmins)("To: " + user.telegram_id + "\nMessage: " + "Привет! Твое сообщение прошло модерацию и будет показываться пользователям. Спасибо за вклад, обнимаю 😍\n\nТут вывести текст, ссылку и картинку сообщения. " + message.text)];
            case 10:
                _e.sent();
                return [3 /*break*/, 12];
            case 11:
                updateToReview.push(calculatedMessage._id);
                _e.label = 12;
            case 12: return [3 /*break*/, 14];
            case 13:
                _a = true;
                return [7 /*endfinally*/];
            case 14: return [3 /*break*/, 6];
            case 15: return [3 /*break*/, 22];
            case 16:
                e_1_1 = _e.sent();
                e_1 = { error: e_1_1 };
                return [3 /*break*/, 22];
            case 17:
                _e.trys.push([17, , 20, 21]);
                if (!(!_a && !_b && (_c = messages_1["return"]))) return [3 /*break*/, 19];
                return [4 /*yield*/, _c.call(messages_1)];
            case 18:
                _e.sent();
                _e.label = 19;
            case 19: return [3 /*break*/, 21];
            case 20:
                if (e_1) throw e_1.error;
                return [7 /*endfinally*/];
            case 21: return [7 /*endfinally*/];
            case 22:
                filterToApproved = {
                    _id: {
                        "$in": updateToApproved
                    }
                };
                filterToReview = {
                    _id: {
                        "$in": updateToReview
                    }
                };
                docToApproved = {
                    $set: {
                        is_approved: true
                    }
                };
                docToReview = {
                    $set: {
                        is_approved: false
                    }
                };
                if (!(updateToApproved.length !== 0)) return [3 /*break*/, 25];
                return [4 /*yield*/, messagesCol.updateMany(filterToApproved, docToApproved)];
            case 23:
                resultApprove = _e.sent();
                resString = "\u041E\u0431\u043D\u043E\u0432\u0438\u043B ".concat(resultApprove.modifiedCount, " \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435(\u0438\u0439) \u043D\u0430 \u0441\u0442\u0430\u0442\u0443\u0441 \"\u0410\u043F\u043F\u0440\u0443\u0432\"");
                console.log(resString);
                return [4 /*yield*/, (0, users_1.sendMessageToAdmins)(resString)];
            case 24:
                _e.sent();
                return [3 /*break*/, 27];
            case 25:
                resString = "\u041D\u0435\u0447\u0435\u0433\u043E \u043E\u0431\u043D\u043E\u0432\u043B\u044F\u0442\u044C \u043D\u0430 \u0441\u0442\u0430\u0442\u0443\u0441 \"\u0410\u043F\u043F\u0440\u0443\u0432\"";
                console.log(resString);
                return [4 /*yield*/, (0, users_1.sendMessageToAdmins)(resString)];
            case 26:
                _e.sent();
                _e.label = 27;
            case 27:
                if (!(updateToReview.length !== 0)) return [3 /*break*/, 30];
                return [4 /*yield*/, messagesCol.updateMany(filterToReview, docToReview)];
            case 28:
                resultReview = _e.sent();
                resString = "\u041E\u0431\u043D\u043E\u0432\u0438\u043B ".concat(resultReview.modifiedCount, " \u0441\u043E\u043E\u0431\u0449\u0435\u043D\u0438\u0435(\u0438\u0439) \u043D\u0430 \u0441\u0442\u0430\u0442\u0443\u0441 \"\u041C\u043E\u0434\u0435\u0440\u0430\u0446\u0438\u044F\"");
                console.log(resString);
                return [4 /*yield*/, (0, users_1.sendMessageToAdmins)(resString)];
            case 29:
                _e.sent();
                return [3 /*break*/, 32];
            case 30:
                resString = "\u041D\u0435\u0447\u0435\u0433\u043E \u043E\u0431\u043D\u043E\u0432\u043B\u044F\u0442\u044C \u043D\u0430 \u0441\u0442\u0430\u0442\u0443\u0441 \"\u041C\u043E\u0434\u0435\u0440\u0430\u0446\u0438\u044F\"";
                console.log(resString);
                return [4 /*yield*/, (0, users_1.sendMessageToAdmins)(resString)];
            case 31:
                _e.sent();
                _e.label = 32;
            case 32: return [2 /*return*/, { update_to_approve: updateToApproved.length, update_to_review: updateToReview.length }];
        }
    });
}); };
exports.getCalculatedRates = getCalculatedRates;
var calculateRate = function (message, settings) {
    var approve_number = settings.approve_number, admin_rate_number = settings.admin_rate_number, volunteer_rate_number = settings.volunteer_rate_number, disaprove_percent = settings.disaprove_percent;
    var _a = __assign({}, message), admin_bad_rates = _a.admin_bad_rates, admin_good_rates = _a.admin_good_rates, user_bad_rates = _a.user_bad_rates, user_good_rates = _a.user_good_rates;
    var total = (admin_bad_rates + admin_good_rates) * admin_rate_number + (user_bad_rates + user_good_rates) * volunteer_rate_number;
    var rate = (admin_good_rates * admin_rate_number) + (user_good_rates * volunteer_rate_number) - (admin_bad_rates * admin_rate_number) - (user_bad_rates * volunteer_rate_number);
    if (total < approve_number) {
        return __assign(__assign({}, message), { is_approved: false });
    }
    if (rate / total > disaprove_percent / 100) {
        return __assign(__assign({}, message), { is_approved: true });
    }
    return __assign(__assign({}, message), { is_approved: false });
};

"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
exports.__esModule = true;
exports.getGreetingsMessage = exports.getMoodMessage = exports.getThatsItMessage = exports.getHurryUpMessage = void 0;
var hurry_up_1 = require("./hurry_up");
__createBinding(exports, hurry_up_1, "default", "getHurryUpMessage");
var thats_it_1 = require("./thats_it");
__createBinding(exports, thats_it_1, "default", "getThatsItMessage");
var mood_1 = require("./mood");
__createBinding(exports, mood_1, "default", "getMoodMessage");
var greetings_1 = require("./greetings");
__createBinding(exports, greetings_1, "default", "getGreetingsMessage");

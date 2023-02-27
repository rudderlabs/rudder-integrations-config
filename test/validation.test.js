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
Object.defineProperty(exports, "__esModule", { value: true });
/* eslint-disable no-console */
/* eslint-disable max-len */
var fs_1 = require("fs");
var path_1 = require("path");
var commander_1 = require("commander");
var src_1 = require("../src");
var command = new commander_1.default.Command();
command
    .allowUnknownOption()
    .option('-d, --destinations <string>', 'Enter destination names separated by comma', 'all')
    .option('-s, --sources <string>', 'Enter source names separated by comma', 'all')
    .parse();
var cmdOpts = command.opts();
function getIntegrationNames(type) {
    var dirPath = path_1.default.resolve("src/configurations/".concat(type));
    return fs_1.default.readdirSync(dirPath).filter(function (file) { return fs_1.default.statSync("".concat(dirPath, "/").concat(file)).isDirectory(); });
}
function getIntegrationData(name, type) {
    var intgData;
    try {
        intgData = JSON.parse(fs_1.default.readFileSync(path_1.default.resolve(__dirname, "./data/validation/".concat(type, "/").concat(name, ".json")), 'utf-8'));
    }
    catch (e) {
        // console.error(e);
        // console.error(`Unable to load test data for: "${name}" (${type})`);
    }
    return intgData;
}
var destList = [];
if (cmdOpts.destinations !== 'all') {
    destList = cmdOpts.destinations
        .split(',')
        .map(function (x) { return x.trim(); })
        .filter(function (x) { return x; });
    console.log("Destinations specified: ".concat(destList));
}
else {
    destList = getIntegrationNames('destinations');
}
var destTcData = {};
destList.forEach(function (d) {
    var intgData = getIntegrationData(d, 'destinations');
    if (intgData)
        destTcData[d] = intgData;
});
var srcList = [];
if (cmdOpts.sources !== 'all') {
    srcList = cmdOpts.sources
        .split(',')
        .map(function (x) { return x.trim(); })
        .filter(function (x) { return x; });
    console.log("Sources specified: ".concat(srcList));
}
else {
    srcList = getIntegrationNames('sources');
}
var srcTcData = {};
srcList.forEach(function (s) {
    var intgData = getIntegrationData(s, 'sources');
    if (intgData)
        srcTcData[s] = intgData;
});
describe('Core Tests', function () {
    it('If invalid integration name is provide, throw error', function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            expect(function () {
                (0, src_1.validateConfig)('', {}, 'destinations', true);
            }).toThrow('Missing definitionName');
            return [2 /*return*/];
        });
    }); });
    it('If unknown integration name is provided, throw error', function () { return __awaiter(void 0, void 0, void 0, function () {
        var invalidIntg;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, src_1.init)()];
                case 1:
                    _a.sent();
                    invalidIntg = 'INVALID_INTEGRATION_NAME';
                    expect(function () {
                        (0, src_1.validateConfig)(invalidIntg, {}, 'destinations', true);
                    }).toThrow("No validation method found for definition ".concat(invalidIntg));
                    return [2 /*return*/];
            }
        });
    }); });
    it('If unknown integration name is provided and throw errors flag is disabled, no error should be thrown', function () { return __awaiter(void 0, void 0, void 0, function () {
        var invalidIntg;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, src_1.init)()];
                case 1:
                    _a.sent();
                    invalidIntg = 'INVALID_INTEGRATION_NAME';
                    expect(function () {
                        (0, src_1.validateConfig)(invalidIntg, {}, 'destinations');
                    }).not.toThrow();
                    return [2 /*return*/];
            }
        });
    }); });
});
describe('Validation Tests', function () {
    beforeAll(function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, src_1.init)()];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    }); });
    // Destination tests
    Object.keys(destTcData).forEach(function (dest, destIdx) {
        describe("".concat(destIdx + 1, ". Destination - ").concat(dest), function () {
            destTcData[dest].forEach(function (td, tcIdx) {
                it("TC ".concat(tcIdx + 1), function () { return __awaiter(void 0, void 0, void 0, function () {
                    return __generator(this, function (_a) {
                        if (td.result === true) {
                            expect((0, src_1.validateConfig)(dest, td.config, 'destinations', true)).toBeUndefined();
                        }
                        else {
                            expect(function () {
                                (0, src_1.validateConfig)(dest, td.config, 'destinations', true);
                            }).toThrow(JSON.stringify(td.err));
                        }
                        return [2 /*return*/];
                    });
                }); });
            });
        });
    });
    // Source tests
    Object.keys(srcTcData).forEach(function (src, srcIdx) {
        describe("".concat(srcIdx + 1, ". Source - ").concat(src), function () {
            srcTcData[src].forEach(function (td, tcIdx) {
                it("TC ".concat(tcIdx + 1), function () { return __awaiter(void 0, void 0, void 0, function () {
                    return __generator(this, function (_a) {
                        if (td.result === true) {
                            expect((0, src_1.validateConfig)(src, td.config, 'sources', true)).toBeUndefined();
                        }
                        else {
                            expect(function () {
                                (0, src_1.validateConfig)(src, td.config, 'sources', true);
                            }).toThrow(JSON.stringify(td.err));
                        }
                        return [2 /*return*/];
                    });
                }); });
            });
        });
    });
});

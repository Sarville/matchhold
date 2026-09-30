// Minimal self-check for server.js: launch-auth gate, entitlement ledger, payments webhook (VK+OK),
// savegames. Run: `node ops/vk-payments/server.test.js`. Guards the money/security path.
const assert = require("assert");
const crypto = require("crypto");
const path = require("path");
const fs = require("fs");
const os = require("os");

const APP_SECRET = "test_secret";
const PORT = 34122;
const DATA_FILE = path.join(os.tmpdir(), `vk-payments-mh-test-${Date.now()}.json`);
const SAVEGAMES_DIR = path.join(os.tmpdir(), `vk-payments-mh-test-savegames-${Date.now()}`);

process.env.VK_APP_SECRET = APP_SECRET;
process.env.DATA_FILE = DATA_FILE;
process.env.SAVEGAMES_DIR = SAVEGAMES_DIR;
process.env.PORT = String(PORT);

const { server, handleOkPaymentNotification } = require("./server.js");

function signLaunchParams(params) {
    const joined = Object.keys(params)
        .filter(k => k.startsWith("vk_"))
        .sort()
        .map(k => `${k}=${params[k]}`)
        .join("&");
    return crypto
        .createHmac("sha256", APP_SECRET)
        .update(joined)
        .digest("base64")
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

function launchQuery(vkUserId, overrides = {}) {
    const params = { vk_user_id: vkUserId, vk_ts: String(Math.floor(Date.now() / 1000)), ...overrides };
    return new URLSearchParams({ ...params, sign: signLaunchParams(params) }).toString();
}

function signPaymentParams(params) {
    const joined = Object.keys(params)
        .sort()
        .map(key => `${key}=${params[key]}`)
        .join("");
    return crypto.createHash("md5").update(joined + APP_SECRET).digest("hex");
}

const form = params => new URLSearchParams({ ...params, sig: signPaymentParams(params) }).toString();

function fakeRes() {
    return {
        status: null,
        headers: null,
        body: null,
        writeHead(status, headers) {
            this.status = status;
            this.headers = headers;
        },
        end(body) {
            this.body = body;
        },
    };
}

async function request(method, urlPath, body, headers) {
    const res = await fetch(`http://127.0.0.1:${PORT}${urlPath}`, {
        method,
        body,
        headers: { ...(body ? { "Content-Type": "application/x-www-form-urlencoded" } : {}), ...headers },
    });
    const text = await res.text();
    return { status: res.status, body: text ? JSON.parse(text) : null };
}

async function main() {
    const gameQuery = launchQuery("123");

    // Launch gate
    assert.strictEqual((await request("GET", `/vk/matchhold?${gameQuery}`)).status, 200, "valid launch params pass");
    assert.strictEqual(
        (await request("GET", `/vk/matchhold?${gameQuery}&vk_user_id=999`)).status,
        403,
        "tampered signed param fails"
    );
    assert.strictEqual(
        (await request("GET", `/vk/matchhold?${gameQuery}`, undefined, { Referer: "https://games.sarville.online/vk/matchhold/?x" })).status,
        200,
        "self-referer (reload) passes"
    );
    assert.strictEqual(
        (await request("GET", `/vk/matchhold?${gameQuery}`, undefined, { Referer: "https://evil.example/" })).status,
        403,
        "foreign referer fails"
    );
    const okMsQuery = launchQuery("123", { vk_ts: String(Date.now()), vk_client: "ok" });
    assert.strictEqual((await request("GET", `/vk/matchhold?${okMsQuery}`)).status, 200, "OK millisecond vk_ts passes");
    const staleQuery = launchQuery("123", { vk_ts: String(Math.floor(Date.now() / 1000) - 9 * 3600) });
    assert.strictEqual((await request("GET", `/vk/matchhold?${staleQuery}`)).status, 403, "stale vk_ts fails");

    // Entitlements
    let entitlements = (await request("GET", `/vk/matchhold-entitlements?${gameQuery}`)).body;
    assert.deepStrictEqual(entitlements, { adsDisabled: false }, "new user has no entitlements");
    assert.strictEqual((await request("GET", `/vk/matchhold-entitlements`)).status, 403, "unsigned entitlements rejected");
    assert.strictEqual((await request("GET", `/vk/matchhold-entitlements?${launchQuery("../x")}`)).status, 400, "non-numeric id rejected");
    await request("GET", `/vk/matchhold-entitlements?${launchQuery("424242")}`);

    // get_item (VK, with sandbox _test suffix, and OK with uppercase site)
    const getItemParams = { notification_type: "get_item_test", item: "disable_ads" };
    let r = await request("POST", "/vk/matchhold-payments", form(getItemParams));
    assert.strictEqual(r.body.response.item_id, "disable_ads");
    assert.strictEqual(r.body.response.price, 15, "VK price");
    r = await request("POST", "/vk/matchhold-payments", form({ notification_type: "get_item", item: "disable_ads", site: "OK" }));
    assert.strictEqual(r.body.response.price, 120, "OK price for site=\"OK\"");
    r = await request("POST", "/vk/matchhold-payments", form({ notification_type: "get_item", item: "nope" }));
    assert.strictEqual(r.body.error.error_code, 20, "unknown item rejected");

    // order_status_change credits the user
    const orderParams = { notification_type: "order_status_change", item: "disable_ads", status: "chargeable", order_id: "555", user_id: "123" };
    await request("POST", "/vk/matchhold-payments", form(orderParams));
    entitlements = (await request("GET", `/vk/matchhold-entitlements?${gameQuery}`)).body;
    assert.strictEqual(entitlements.adsDisabled, true, "webhook credits disable_ads");

    // Forged signature must not credit
    const forged = await request(
        "POST",
        "/vk/matchhold-payments",
        new URLSearchParams({ ...orderParams, user_id: "888", sig: "deadbeef" }).toString()
    );
    assert.strictEqual(forged.body.error.error_code, 10, "forged payment signature rejected");
    assert.strictEqual((await request("GET", `/vk/matchhold-entitlements?${launchQuery("888")}`)).body.adsDisabled, false);
    assert.ok(!("424242" in JSON.parse(fs.readFileSync(DATA_FILE, "utf8"))), "GET does not create a ledger record");
    const badUser = { ...orderParams, order_id: "556", user_id: "12/../3" };
    assert.strictEqual(
        (await request("POST", "/vk/matchhold-payments", form(badUser))).body.error.error_code,
        20,
        "non-numeric payer id rejected"
    );

    // OK confirmation
    const okParams = { uid: "777", transaction_id: "ok-1", transaction_time: "2026-09-15 12:00:00", amount: "120", product_code: "disable_ads" };
    const okRes = fakeRes();
    await handleOkPaymentNotification(new URLSearchParams({ ...okParams, sig: signPaymentParams(okParams) }), okRes);
    assert.strictEqual(okRes.body, "true", "valid OK confirmation returns bare true");
    assert.strictEqual((await request("GET", `/vk/matchhold-entitlements?${launchQuery("777", { vk_client: "ok" })}`)).body.adsDisabled, true);
    assert.strictEqual((await request("GET", `/vk/matchhold-entitlements?${launchQuery("777")}`)).body.adsDisabled, false, "OK purchase does not leak to the VK user with the same id");

    const badSigRes = fakeRes();
    await handleOkPaymentNotification(new URLSearchParams({ ...okParams, sig: "deadbeef" }), badSigRes);
    assert.strictEqual(badSigRes.headers["Invocation-error"], "1001", "forged OK signature rejected");

    const wrongPrice = { ...okParams, uid: "778", transaction_id: "ok-2", amount: "1" };
    const wrongPriceRes = fakeRes();
    await handleOkPaymentNotification(new URLSearchParams({ ...wrongPrice, sig: signPaymentParams(wrongPrice) }), wrongPriceRes);
    assert.strictEqual(JSON.parse(wrongPriceRes.body).error_code, 1001, "OK amount must match priceOk");
    assert.strictEqual((await request("GET", `/vk/matchhold-entitlements?${launchQuery("778")}`)).body.adsDisabled, false);

    // Rate limit: 60 requests/min per user
    const rateQ = launchQuery("5150");
    let last = 200;
    for (let i = 0; i < 61; i++) {
        last = (await request("GET", `/vk/matchhold-entitlements?${rateQ}`)).status;
    }
    assert.strictEqual(last, 429, "61st request within a minute is throttled");

    // Savegames
    const saveQuery = launchQuery("321");
    assert.strictEqual((await request("GET", `/vk/matchhold-savegames?${saveQuery}`)).body, null, "no save yet");
    const bundle = JSON.stringify({ ts: 1, data: { slot0: "{}", gameOptions: "{}" } });
    const post = (q, body) =>
        fetch(`http://127.0.0.1:${PORT}/vk/matchhold-savegames?${q}`, { method: "POST", body, headers: { "Content-Type": "application/json" } });
    assert.strictEqual((await post(saveQuery, bundle)).status, 200);
    assert.deepStrictEqual((await request("GET", `/vk/matchhold-savegames?${saveQuery}`)).body, JSON.parse(bundle), "save round-trips");
    assert.strictEqual((await post(saveQuery.replace("321", "999"), bundle)).status, 403, "tampered vk_user_id rejected");
    assert.strictEqual((await post(saveQuery, "not json")).status, 400, "non-JSON rejected");
    assert.strictEqual((await post(saveQuery, "[1]")).status, 400, "wrong shape rejected");
    assert.strictEqual((await post(saveQuery, JSON.stringify({ ts: 1, data: { "../evil": "x" } }))).status, 400, "foreign keys rejected");
    assert.strictEqual((await post(saveQuery, JSON.stringify({ ts: 1, data: { slot0: { a: 1 } } }))).status, 400, "non-string value rejected");
    const okSaveQuery = launchQuery("321", { vk_client: "ok" });
    assert.strictEqual((await request("GET", `/vk/matchhold-savegames?${okSaveQuery}`)).body, null, "OK user does not see VK user's save");
    assert.strictEqual((await post(saveQuery, "[" + "0,".repeat(1.2e6) + "0]")).status, 413, "oversized rejected");

    console.log("All vk-payments server checks passed.");
}

main()
    .catch(err => {
        console.error(err);
        process.exitCode = 1;
    })
    .finally(() => {
        server.close();
        fs.rmSync(DATA_FILE, { force: true });
        fs.rmSync(SAVEGAMES_DIR, { recursive: true, force: true });
    });

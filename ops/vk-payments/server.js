const http = require("http");
const fs = require("fs");
const crypto = require("crypto");

const APP_SECRET = process.env.VK_APP_SECRET || "";

// Entitlement ledger keyed by vk_user_id: VK has no client-side "my purchases" API, so this file
// (built from the payments webhook) is the only record of who bought disable_ads. Bind-mount /data.
const DATA_FILE = process.env.DATA_FILE || "/data/entitlements.json";
const SAVEGAMES_DIR = process.env.SAVEGAMES_DIR || "/data/savegames";
fs.mkdirSync(SAVEGAMES_DIR, { recursive: true });

// ponytail: flat 2 MB cap (3 slots + options as text JSON), raise if real saves hit it.
const MAX_SAVEGAME_BYTES = 2 * 1024 * 1024;

const isValidVkUserId = id => typeof id === "string" && /^[0-9]+$/.test(id); // also keeps it path-safe

// price = VK "голоса", priceOk = OK "ОКи". They don't convert 1:1 to RUB or to each other - take
// the rate from the cabinet's purchase storefront (see ops/README.md), never guess.
const ITEMS = {
    disable_ads: {
        title: "Отключить рекламу",
        price: Number(process.env.ITEM_PRICE_VK) || 10,
        priceOk: Number(process.env.ITEM_PRICE_OK) || 30,
    },
};

let entitlements = {};
try {
    entitlements = JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
} catch {
    entitlements = {};
}

// Serializes writes so retried webhooks can't race each other's write of the same file.
let writeQueue = Promise.resolve();
function persist() {
    const write = () => fs.promises.writeFile(DATA_FILE, JSON.stringify(entitlements));
    writeQueue = writeQueue.then(write, write);
    return writeQueue;
}

function getUser(vkUserId) {
    if (!entitlements[vkUserId]) {
        entitlements[vkUserId] = { adsDisabled: false };
    }
    return entitlements[vkUserId];
}

// Classic Payments API signature: md5 of all params except sig, sorted, "name=value" concatenated
// with no separator, plus the app secret. (Launch params below use a different scheme.)
function isValidSig(params) {
    if (!APP_SECRET) {
        return false;
    }
    const { sig, ...rest } = params;
    const joined = Object.keys(rest)
        .sort()
        .map(key => `${key}=${rest[key]}`)
        .join("");
    return sig === crypto.createHash("md5").update(joined + APP_SECRET).digest("hex");
}

// Launch-params signature: HMAC-SHA256 over the vk_ params, base64url. Proves a fresh VK/OK launch.
const LAUNCH_MAX_AGE_SECONDS = 8 * 60 * 60;

function isValidLaunchParams(searchParams) {
    if (!APP_SECRET) {
        return false;
    }
    const sign = searchParams.get("sign");
    if (!sign) {
        return false;
    }
    const joined = [...searchParams.keys()]
        .filter(k => k.startsWith("vk_"))
        .sort()
        .map(k => `${k}=${searchParams.get(k)}`)
        .join("&");
    const expected = crypto
        .createHmac("sha256", APP_SECRET)
        .update(joined)
        .digest("base64")
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
    if (expected !== sign) {
        return false;
    }
    // OK sends vk_ts in milliseconds, VK in seconds; anything > 1e11 is unambiguously ms.
    let ts = Number(searchParams.get("vk_ts"));
    if (ts > 1e11) {
        ts /= 1000;
    }
    const age = Date.now() / 1000 - ts;
    return Boolean(ts) && age >= -60 && age <= LAUNCH_MAX_AGE_SECONDS;
}

// Soft check only: a missing Referer passes, a present-but-foreign one fails. The game's own host
// must be allowed: a language-change location.reload() sends the game's own URL as Referer.
function isAcceptableReferer(referer) {
    if (!referer) {
        return true;
    }
    try {
        const host = new URL(referer).hostname;
        return (
            host === "vk.com" ||
            host.endsWith(".vk.com") ||
            host === "vk.ru" ||
            host.endsWith(".vk.ru") ||
            host === "ok.ru" ||
            host.endsWith(".ok.ru") ||
            host === "games.sarville.online"
        );
    } catch {
        return false;
    }
}

// OK's own purchase confirmation (GET, separate "URL для платёжных уведомлений Одноклассников").
// Same app secret/sig formula. Success = bare JSON `true`; failure = error JSON + Invocation-error.
async function handleOkPaymentNotification(searchParams, res) {
    const params = Object.fromEntries(searchParams);

    function fail(code, msg) {
        res.writeHead(200, { "Content-Type": "application/json", "Invocation-error": String(code) });
        res.end(JSON.stringify({ error_code: code, error_msg: msg, error_data: null }));
    }

    if (!isValidSig(params)) {
        return fail(1001, "CALLBACK_INVALID_SIGNATURE: invalid sig");
    }
    if (!params.uid || !params.transaction_id || !params.transaction_time || !params.amount) {
        return fail(1001, "CALLBACK_INVALID_PAYMENT: missing required field");
    }
    const item = ITEMS[params.product_code];
    if (!item || Number(params.amount) !== item.priceOk) {
        return fail(1001, "CALLBACK_INVALID_PAYMENT: unknown item or price");
    }

    getUser(params.uid).adsDisabled = true;
    await persist();

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end("true");
}

// Over the cap the body is drained (not stored) and rejected at the end, so the client gets a clean
// 413 instead of a connection reset.
function readBody(req, maxBytes = Infinity) {
    return new Promise((resolve, reject) => {
        let body = "";
        let bytes = 0;
        req.on("data", chunk => {
            bytes += chunk.length;
            if (bytes <= maxBytes) {
                body += chunk;
            }
        });
        req.on("end", () =>
            bytes > maxBytes ? reject(Object.assign(new Error("payload too large"), { tooLarge: true })) : resolve(body)
        );
        req.on("error", reject);
    });
}

const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, "http://placeholder");

    // Gate for the game page itself: Caddy forward_auth mirrors the request here first.
    if (req.method === "GET" && (url.pathname === "/vk/matchhold" || url.pathname === "/vk/matchhold/")) {
        const ok = isValidLaunchParams(url.searchParams) && isAcceptableReferer(req.headers.referer);
        res.writeHead(ok ? 200 : 403);
        return res.end();
    }

    if (req.method === "GET" && url.pathname === "/vk/matchhold-entitlements") {
        if (!isValidLaunchParams(url.searchParams)) {
            res.writeHead(403);
            return res.end();
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        return res.end(JSON.stringify(getUser(url.searchParams.get("vk_user_id"))));
    }

    // Cross-device progress (VK rule 2.3.8): one JSON blob per user, never held in memory.
    if (url.pathname === "/vk/matchhold-savegames" && (req.method === "GET" || req.method === "POST")) {
        if (!isValidLaunchParams(url.searchParams)) {
            res.writeHead(403);
            return res.end();
        }
        const vkUserId = url.searchParams.get("vk_user_id");
        if (!isValidVkUserId(vkUserId)) {
            res.writeHead(400);
            return res.end();
        }
        const file = `${SAVEGAMES_DIR}/${vkUserId}.json`;
        if (req.method === "GET") {
            res.writeHead(200, { "Content-Type": "application/json" });
            return res.end(await fs.promises.readFile(file, "utf8").catch(() => "null"));
        }
        let body;
        try {
            body = await readBody(req, MAX_SAVEGAME_BYTES);
            JSON.parse(body); // reject non-JSON before persisting
        } catch (ex) {
            res.writeHead(ex.tooLarge ? 413 : 400);
            return res.end();
        }
        await fs.promises.writeFile(file, body);
        res.writeHead(200);
        return res.end();
    }

    if (req.method === "GET" && url.pathname === "/vk/matchhold-payments/ok") {
        return await handleOkPaymentNotification(url.searchParams, res);
    }

    // VK payments callback (get_item / order_status_change), also receives OK's get_item.
    if (req.method === "POST" && url.pathname === "/vk/matchhold-payments") {
        const body = await readBody(req, 64 * 1024).catch(() => "");
        const params = Object.fromEntries(new URLSearchParams(body));
        res.writeHead(200, { "Content-Type": "application/json" });

        if (!isValidSig(params)) {
            return res.end(JSON.stringify({ error: { error_code: 10, error_msg: "Invalid signature" } }));
        }

        // The cabinet's "Тестовый" button appends "_test" to notification_type.
        const notificationType = (params.notification_type || "").replace(/_test$/, "");
        const item = ITEMS[params.item];

        if (notificationType === "get_item" && item) {
            // OK sends site="OK" (uppercase) - compare case-insensitively.
            const price = (params.site || "").toLowerCase() === "ok" ? item.priceOk : item.price;
            return res.end(JSON.stringify({ response: { title: item.title, price, item_id: params.item } }));
        }

        if (notificationType === "order_status_change" && params.status === "chargeable" && item) {
            getUser(params.user_id).adsDisabled = true;
            await persist();
            return res.end(
                JSON.stringify({ response: { order_id: Number(params.order_id), app_order_id: Number(params.order_id) } })
            );
        }

        return res.end(JSON.stringify({ error: { error_code: 20, error_msg: "Unknown item or notification" } }));
    }

    res.writeHead(404);
    res.end();
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`vk-payments-matchhold listening on :${PORT}`));

module.exports = { server, isValidSig, isValidLaunchParams, isAcceptableReferer, handleOkPaymentNotification };

const http = require("http");
const fs = require("fs");
const crypto = require("crypto");

const APP_SECRET = process.env.VK_APP_SECRET || "";

// Entitlement ledger keyed by vk_user_id: VK has no client-side "my purchases" API, so this file
// (built from the payments webhook) is the only record of who bought disable_ads. Bind-mount /data.
const DATA_FILE = process.env.DATA_FILE || "/data/entitlements.json";
const SAVEGAMES_DIR = process.env.SAVEGAMES_DIR || "/data/savegames";
fs.mkdirSync(SAVEGAMES_DIR, { recursive: true });
// Files used to be <id>.json; VK and OK ids can collide, so they are now <vk|ok>_<id>.json. Old files were VK-era.
for (const f of fs.readdirSync(SAVEGAMES_DIR)) {
    if (/^[0-9]+\.json$/.test(f)) {
        fs.renameSync(`${SAVEGAMES_DIR}/${f}`, `${SAVEGAMES_DIR}/vk_${f}`);
    }
}

// ponytail: flat 2 MB cap (3 slots + options as text JSON), raise if real saves hit it.
const MAX_SAVEGAME_BYTES = 2 * 1024 * 1024;

const isValidVkUserId = id => typeof id === "string" && /^[0-9]+$/.test(id); // also keeps it path-safe

// Constant-time string compare for signatures.
function safeEqual(a, b) {
    const x = Buffer.from(String(a));
    const y = Buffer.from(String(b));
    return x.length === y.length && crypto.timingSafeEqual(x, y);
}

// Only what the client really syncs (platform.js snapshot): { ts, data: { slotN | gameOptions: string } }.
function isValidSavegame(body) {
    let blob;
    try {
        blob = JSON.parse(body);
    } catch {
        return false;
    }
    if (!blob || typeof blob !== "object" || typeof blob.ts !== "number" || !blob.data || typeof blob.data !== "object") {
        return false;
    }
    return Object.entries(blob.data).every(
        ([k, v]) => (/^slot[0-9]+$/.test(k) || k === "gameOptions") && typeof v === "string"
    );
}

// price = VK "голоса", priceOk = OK "ОКи". They don't convert 1:1 to RUB or to each other - take
// the rate from the cabinet's purchase storefront (see ops/README.md), never guess.
const ITEMS = {
    disable_ads: {
        title: "Отключить рекламу",
        price: Number(process.env.ITEM_PRICE_VK) || 15,
        priceOk: Number(process.env.ITEM_PRICE_OK) || 120,
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
// tmp + rename: a crash mid-write must not leave a truncated file
async function writeFileAtomic(file, data) {
    const tmp = `${file}.${process.pid}.${crypto.randomBytes(4).toString("hex")}.tmp`;
    await fs.promises.writeFile(tmp, data);
    await fs.promises.rename(tmp, file);
}
function persist() {
    const write = () => writeFileAtomic(DATA_FILE, JSON.stringify(entitlements));
    writeQueue = writeQueue.then(write, write);
    return writeQueue;
}

// VK and OK user ids can collide, so the ledger is keyed <vk|ok>_<id> (same as savegames).
const clientOf = v => (String(v).toLowerCase() === "ok" ? "ok" : "vk");

// Read-only: a GET must never create a ledger record.
function readUser(client, id) {
    return entitlements[`${client}_${id}`] || { adsDisabled: false };
}

function getUser(client, id) {
    const key = `${client}_${id}`;
    if (!entitlements[key]) {
        entitlements[key] = { adsDisabled: false };
    }
    return entitlements[key];
}

// ponytail: fixed window per user, in memory, reset on restart; move to a Caddy rate_limit module if abused.
const RATE_MAX_PER_MIN = 60;
const rateHits = new Map();
function rateOk(key) {
    const now = Date.now();
    let h = rateHits.get(key);
    if (!h || now > h.reset) {
        h = { n: 0, reset: now + 60000 };
        rateHits.set(key, h);
    }
    return ++h.n <= RATE_MAX_PER_MIN;
}
setInterval(() => {
    const now = Date.now();
    for (const [k, h] of rateHits) {
        if (now > h.reset) {
            rateHits.delete(k);
        }
    }
}, 60000).unref();

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
    return typeof sig === "string" && safeEqual(sig, crypto.createHash("md5").update(joined + APP_SECRET).digest("hex"));
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
    if (!safeEqual(expected, sign)) {
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
    if (!isValidVkUserId(params.uid) || !params.transaction_id || !params.transaction_time || !params.amount) {
        return fail(1001, "CALLBACK_INVALID_PAYMENT: missing required field");
    }
    const item = ITEMS[params.product_code];
    if (!item || Number(params.amount) !== item.priceOk) {
        return fail(1001, "CALLBACK_INVALID_PAYMENT: unknown item or price");
    }

    getUser("ok", params.uid).adsDisabled = true;
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

async function handle(req, res) {
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
        const id = url.searchParams.get("vk_user_id");
        if (!isValidVkUserId(id)) {
            res.writeHead(400);
            return res.end();
        }
        if (!rateOk(`e${clientOf(url.searchParams.get("vk_client"))}_${id}`)) {
            res.writeHead(429);
            return res.end();
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        return res.end(JSON.stringify(readUser(clientOf(url.searchParams.get("vk_client")), id)));
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
        const client = clientOf(url.searchParams.get("vk_client"));
        if (!rateOk(`s${client}_${vkUserId}`)) {
            res.writeHead(429);
            return res.end();
        }
        const file = `${SAVEGAMES_DIR}/${client}_${vkUserId}.json`;
        if (req.method === "GET") {
            res.writeHead(200, { "Content-Type": "application/json" });
            return res.end(await fs.promises.readFile(file, "utf8").catch(() => "null"));
        }
        let body;
        try {
            body = await readBody(req, MAX_SAVEGAME_BYTES);
        } catch (ex) {
            res.writeHead(ex.tooLarge ? 413 : 400);
            return res.end();
        }
        if (!isValidSavegame(body)) {
            res.writeHead(400);
            return res.end();
        }
        await writeFileAtomic(file, body);
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
            if (!isValidVkUserId(params.user_id)) {
                return res.end(JSON.stringify({ error: { error_code: 20, error_msg: "Bad user_id" } }));
            }
            getUser(clientOf(params.site), params.user_id).adsDisabled = true;
            await persist();
            return res.end(
                JSON.stringify({ response: { order_id: Number(params.order_id), app_order_id: Number(params.order_id) } })
            );
        }

        return res.end(JSON.stringify({ error: { error_code: 20, error_msg: "Unknown item or notification" } }));
    }

    res.writeHead(404);
    res.end();
}

const server = http.createServer(async (req, res) => {
    try {
        await handle(req, res);
    } catch (err) {
        console.error(err);
        if (!res.headersSent) {
            res.writeHead(500);
        }
        res.end();
    }
});

process.on("unhandledRejection", err => console.error("unhandledRejection", err));

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`vk-payments-matchhold listening on :${PORT}`));

module.exports = { server, isValidSig, isValidLaunchParams, isAcceptableReferer, handleOkPaymentNotification };

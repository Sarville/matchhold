package ru.sarville.matchhold;

import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.List;

import ru.rustore.sdk.core.tasks.Task;
import ru.rustore.sdk.pay.PurchaseInteractor;
import ru.rustore.sdk.pay.RuStorePayClient;
import ru.rustore.sdk.pay.model.AcknowledgementState;
import ru.rustore.sdk.pay.model.PreferredPurchaseType;
import ru.rustore.sdk.pay.model.ProductId;
import ru.rustore.sdk.pay.model.ProductPurchase;
import ru.rustore.sdk.pay.model.ProductPurchaseParams;
import ru.rustore.sdk.pay.model.ProductPurchaseResult;
import ru.rustore.sdk.pay.model.Purchase;
import ru.rustore.sdk.pay.model.PurchaseId;
import ru.rustore.sdk.pay.model.SdkTheme;

// Тонкий мост к RuStore Pay SDK (Kotlin: необязательные параметры из Java передаём явным null).
// Решения (что считать покупкой) принимает www/js/app/platform/android.js.
@CapacitorPlugin(name = "RuStorePay")
public class RuStorePayPlugin extends Plugin {

    private PurchaseInteractor purchases() {
        return RuStorePayClient.Companion.getInstance().getPurchaseInteractor();
    }

    private static void fail(PluginCall call, Throwable e) {
        call.reject(String.valueOf(e.getMessage()), e instanceof Exception ? (Exception) e : null);
    }

    // ID рекламных блоков зашиты сборкой (gradle.properties / -P), JS берёт их отсюда.
    @PluginMethod
    public void getConfig(PluginCall call) {
        JSObject o = new JSObject();
        o.put("bannerId", BuildConfig.YANDEX_BANNER_ID);
        o.put("interstitialId", BuildConfig.YANDEX_INTERSTITIAL_ID);
        o.put("rewardedId", BuildConfig.YANDEX_REWARDED_ID);
        call.resolve(o);
    }

    @PluginMethod
    public void getPurchases(PluginCall call) {
        try {
            Task<List<Purchase>> task = purchases().getPurchases(null, null, null);
            task.addOnSuccessListener(list -> {
                JSArray out = new JSArray();
                for (Purchase p : list) {
                    if (!(p instanceof ProductPurchase)) {
                        continue;
                    }
                    ProductPurchase pp = (ProductPurchase) p;
                    JSObject o = new JSObject();
                    o.put("purchaseId", pp.getPurchaseId().getValue());
                    o.put("productId", pp.getProductId().getValue());
                    o.put("productType", pp.getProductType().name());
                    o.put("status", pp.getStatus().name());
                    o.put("acknowledgement", pp.getAcknowledgementState().name());
                    out.put(o);
                }
                JSObject result = new JSObject();
                result.put("purchases", out);
                call.resolve(result);
            }).addOnFailureListener(e -> fail(call, e));
        } catch (Exception e) {
            fail(call, e);
        }
    }

    @PluginMethod
    public void purchase(PluginCall call) {
        String productId = call.getString("productId");
        if (productId == null) {
            call.reject("productId is required");
            return;
        }
        try {
            ProductPurchaseParams params = new ProductPurchaseParams(new ProductId(productId), null, null, null, null, null);
            Task<ProductPurchaseResult> task = purchases().purchase(params, PreferredPurchaseType.ONE_STEP, SdkTheme.LIGHT, null);
            task.addOnSuccessListener(r -> {
                JSObject result = new JSObject();
                result.put("purchaseId", r.getPurchaseId().getValue());
                call.resolve(result);
            }).addOnFailureListener(e -> fail(call, e));
        } catch (Exception e) {
            fail(call, e);
        }
    }

    @PluginMethod
    public void acknowledge(PluginCall call) {
        String purchaseId = call.getString("purchaseId");
        if (purchaseId == null) {
            call.reject("purchaseId is required");
            return;
        }
        try {
            Task<AcknowledgementState> task = purchases().updateAcknowledgementState(new PurchaseId(purchaseId), AcknowledgementState.ACKNOWLEDGED, null);
            task.addOnSuccessListener(s -> call.resolve()).addOnFailureListener(e -> fail(call, e));
        } catch (Exception e) {
            fail(call, e);
        }
    }
}

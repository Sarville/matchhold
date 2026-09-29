package ru.sarville.matchhold;

import android.content.Intent;
import android.os.Bundle;

import androidx.activity.OnBackPressedCallback;

import com.getcapacitor.BridgeActivity;

import ru.rustore.sdk.pay.RuStorePayClient;
import ru.rustore.sdk.pay.model.SdkTheme;

public class MainActivity extends BridgeActivity {
    // «Назад» игры — Escape (ui.js слушает его на document; в главном меню это no-op).
    // Шлём его вместо выхода из приложения.
    private static final String SEND_ESCAPE_JS =
        "['keydown','keyup'].forEach(function(t){document.dispatchEvent(new KeyboardEvent(t,{key:'Escape',code:'Escape',keyCode:27,which:27,bubbles:true}))})";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(RuStorePayPlugin.class);
        super.onCreate(savedInstanceState);
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                getBridge().getWebView().evaluateJavascript(SEND_ESCAPE_JS, null);
            }
        });
        if (savedInstanceState == null) {
            proceedPayIntent(getIntent());
        }
    }

    // Возврат из банковского приложения (СБП/SberPay) приходит deeplink-интентом со схемой из манифеста.
    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        proceedPayIntent(intent);
    }

    private void proceedPayIntent(Intent intent) {
        RuStorePayClient.Companion.getInstance().getIntentInteractor().proceedIntent(intent, SdkTheme.LIGHT);
    }
}

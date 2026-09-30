package ru.sarville.matchhold;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.FrameLayout;

import androidx.activity.OnBackPressedCallback;

import com.airbnb.lottie.LottieAnimationView;
import com.airbnb.lottie.LottieDrawable;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.WebViewListener;

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
            showLottieSplash();
        }
    }

    // Анимированный сплэш поверх WebView: цвет = splash.png, снимается после загрузки страницы (дальше игра
    // показывает свой загрузчик), но не раньше SPLASH_MIN_MS; страховочный таймаут на случай ошибки загрузки.
    private static final int SPLASH_BG = 0xFFEEDCB2;
    private static final long SPLASH_MIN_MS = 1400, SPLASH_MAX_MS = 8000;

    private void showLottieSplash() {
        final FrameLayout content = findViewById(android.R.id.content);
        final FrameLayout overlay = new FrameLayout(this);
        overlay.setBackgroundColor(SPLASH_BG);
        overlay.setClickable(true);
        LottieAnimationView anim = new LottieAnimationView(this);
        anim.setAnimation(R.raw.splash_lottie);
        anim.setRepeatCount(LottieDrawable.INFINITE);
        int size = (int) (Math.min(getResources().getDisplayMetrics().widthPixels, getResources().getDisplayMetrics().heightPixels) * 0.55f);
        overlay.addView(anim, new FrameLayout.LayoutParams(size, size, Gravity.CENTER));
        content.addView(overlay, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        anim.playAnimation();

        final Handler h = new Handler(Looper.getMainLooper());
        final long t0 = System.currentTimeMillis();
        final Runnable hide = new Runnable() {
            boolean done;
            @Override
            public void run() {
                if (done) return;
                done = true;
                overlay.animate().alpha(0f).setDuration(250).withEndAction(() -> {
                    anim.cancelAnimation();
                    content.removeView(overlay);
                }).start();
            }
        };
        h.postDelayed(hide, SPLASH_MAX_MS);
        getBridge().addWebViewListener(new WebViewListener() {
            @Override
            public void onPageLoaded(WebView webView) {
                h.postDelayed(hide, Math.max(0, SPLASH_MIN_MS - (System.currentTimeMillis() - t0)));
            }
        });
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

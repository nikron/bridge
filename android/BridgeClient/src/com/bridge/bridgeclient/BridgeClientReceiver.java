package com.bridge.bridgeclient;

import android.os.ResultReceiver;
import android.os.Handler;
import android.os.Bundle;

public class BridgeClientReceiver extends ResultReceiver
{
    private Receiver mReceiver;

    public BridgeClientReceiver(Handler handler)
    {
        super(handler);
    }

    public interface Receiver
    {
        public void onReceiveResult(int resultCode, Bundle resultData);
    }

    public void setReceiver(Receiver receiver)
    {
        mReceiver = receiver;
    }

    @Override
    protected void onReceiveResult(int resultCode, Bundle resultData)
    {
        if (mReceiver != null)
        {
            mReceiver.onReceiveResult(resultCode, resultData);
        }
    }
}

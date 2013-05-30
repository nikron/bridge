package com.bridge.bridgeclient;

import android.os.ResultReceiver;
import android.os.Handler;
import android.os.Bundle;

public class BridgeClientReceiver extends ResultReceiver
{
    private Receiver receiver;

    public BridgeClientReceiver(Handler handler)
    {
        super(handler);
    }

    interface Receiver
    {
        void onReceiveResult(int resultCode, Bundle resultData);
    }

    public void setReceiver(Receiver receiver)
    {
        this.receiver = receiver;
    }

    @Override
    protected void onReceiveResult(int resultCode, Bundle resultData)
    {
        if (receiver != null)
        {
            receiver.onReceiveResult(resultCode, resultData);
        }
    }
}

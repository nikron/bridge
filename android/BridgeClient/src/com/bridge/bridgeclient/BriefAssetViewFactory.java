package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.RelativeLayout;
import android.widget.TextView;

import android.view.LayoutInflater;
import android.view.View;

public class BriefAssetViewFactory
{
    protected Context context;
    protected Asset asset;
    protected PatchHandler handler;

    public BriefAssetViewFactory(Context context, Asset asset, PatchHandler handler)
    {
        this.context = context;
        this.asset = asset;
        this.handler = handler;
    }

    interface PatchHandler
    {
        void sendAssetPatch(String url, String patch);
    }

    public View getView()
    {
        RelativeLayout layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_unknown, null, false);

        setName(layout);

        return layout;
    }

    protected void setName(RelativeLayout layout)
    {
        TextView assetName = (TextView) layout.findViewById(R.id.assetname);
        assetName.setText(asset.toString());
    }
}

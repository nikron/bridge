package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.CompoundButton;
import android.widget.RelativeLayout;

import android.view.LayoutInflater;
import android.view.View;

import org.jraf.android.backport.switchwidget.Switch;

public class BriefBinaryAssetViewFactory extends BriefAssetViewFactory
{
    public BriefBinaryAssetViewFactory(Context context, Asset asset, PatchHandler handler)
    {
        super(context, asset, handler);
    }

    @Override
    public View getView()
    {
        final State mainState = asset.getMainState();
        RelativeLayout layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_binary, null, false);

        Switch mainSwitch = (Switch) layout.findViewById(R.id.assetcontrol);
        mainSwitch.setEnabled(mainState.isEnabled());
        mainSwitch.setChecked(mainState.getCurrent());

        mainSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                String message = mainState.setState(isChecked);
                handler.sendAssetPatch(asset.getURL(), message);
            }});

        setName(layout);

        return layout;
    }
}

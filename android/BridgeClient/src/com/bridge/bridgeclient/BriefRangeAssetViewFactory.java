package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.RelativeLayout;
import android.widget.SeekBar;

import android.view.LayoutInflater;
import android.view.View;

public class BriefRangeAssetViewFactory extends BriefAssetViewFactory
{
    public BriefRangeAssetViewFactory(Context context, Asset asset, PatchHandler handler)
    {
        super(context, asset, handler);
    }

    @Override
    public View getView()
    {
        final State mainState = asset.getMainState();
        RelativeLayout layout = (RelativeLayout) LayoutInflater.from(context).inflate(R.xml.asset_range, null, false);

        SeekBar mainSeekBar = (SeekBar) layout.findViewById(R.id.assetcontrol);
        mainSeekBar.setEnabled(mainState.isEnabled());
        mainSeekBar.setMax(mainState.getMax() - mainState.getMin());
        mainSeekBar.setProgress(mainState.getCurrentInt());
        mainSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                String message = mainState.setState(progress + mainState.getMin());
                handler.sendAssetPatch(asset.getURL(), message);
            }
            public void onStartTrackingTouch(SeekBar seekBar) {
            }
            public void onStopTrackingTouch(SeekBar seekBar) {
            }
        });

        setName(layout);

        return layout;
    }
}

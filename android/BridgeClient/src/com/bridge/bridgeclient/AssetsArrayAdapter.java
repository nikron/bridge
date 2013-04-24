package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.ArrayAdapter;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import org.jraf.android.backport.switchwidget.Switch;
//import android.widget.Switch;

import android.widget.CompoundButton;

public class AssetsArrayAdapter extends ArrayAdapter<Asset>
{
    final Context context;
    final AssetsFragment fragment;
    static final int binaryAsset = R.xml.asset_binary;
    static final int rangeAsset = R.xml.asset_range;
    static final int textViewResourceId = R.id.assetname;
    static final int controlResourceId = R.id.assetcontrol;

    public AssetsArrayAdapter(Context context, AssetsFragment fragment)
    {
        super(context, binaryAsset, textViewResourceId);
        this.context = context;
        this.fragment = fragment;
    }

    @Override
    public View getView (int position, View convertView, ViewGroup parent)
    {
        final Asset asset = getItem(position);
        RelativeLayout layout;

        switch (asset.getMainType())
        {
            case State.BINARY_TYPE:
            default:
                layout = (RelativeLayout) LayoutInflater.from(context).inflate(binaryAsset, parent, false);
                Switch mainSwitch = (Switch) layout.findViewById(controlResourceId);;
                mainSwitch.setEnabled(asset.isMainEnabled());
                mainSwitch.setChecked(asset.getCurrentMainState());
                mainSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                        String message = asset.setCurrentMainState(isChecked);
                        fragment.sendAssetPatch(asset.getURL(), message);
                }});
                break;
        }

        TextView assetName = (TextView) layout.findViewById(textViewResourceId);
        assetName.setText(asset.toString());

        return layout;
    }
}

package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.ArrayAdapter;
import android.widget.RelativeLayout;
import android.widget.TextView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import org.jraf.android.backport.switchwidget.Switch;
//import android.widget.Switch;

import android.widget.CompoundButton;

public class AssetsArrayAdapter extends ArrayAdapter<Asset> implements CompoundButton.OnCheckedChangeListener
{
    Context context;
    static final int binaryAsset = R.xml.asset_binary;
    static final int rangeAsset = R.xml.asset_range;
    static final int textViewResourceId = R.id.assetname;
    static final int controlResourceId = R.id.assetcontrol;

    public AssetsArrayAdapter(Context context)
    {
        super(context, binaryAsset, textViewResourceId);
        this.context = context;
    }

    /*
    @Override
    public void add(Asset asset)
    {
        super.add(asset);
    }
    */

    @Override
    public View getView (int position, View convertView, ViewGroup parent)
    {
        Asset asset = getItem(position);
        RelativeLayout layout;

        switch (asset.getMainType())
        {
            case State.BINARY_TYPE:
            default:
                layout = (RelativeLayout) LayoutInflater.from(context).inflate(binaryAsset, parent, false);
                Switch mainSwitch = (Switch) layout.findViewById(controlResourceId);;
                mainSwitch.setEnabled(asset.isMainEnabled());
                break;
        }

        TextView assetName = (TextView) layout.findViewById(textViewResourceId);
        assetName.setText(asset.toString());

        return layout;
    }

    @Override
    public void onCheckedChanged(CompoundButton buttonView, boolean isChecked)
    {
    }
}

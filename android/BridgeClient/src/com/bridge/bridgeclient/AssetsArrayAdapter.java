package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.ArrayAdapter;
import android.widget.RelativeLayout;
import android.widget.TextView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import org.jraf.android.backport.switchwidget.Switch; //should figure out if we need this
// or other

public class AssetsArrayAdapter extends ArrayAdapter<Asset>
{
    Context context;
    int resource;
    int textViewResourceId;

    public AssetsArrayAdapter(Context context, int resource, int textViewResourceId)
    {
        super(context, resource, textViewResourceId);
        this.context = context;
        this.resource = resource;
        this.textViewResourceId = textViewResourceId;
    }

    @Override
    public void add(Asset asset)
    {
        super.add(asset);
    }

    @Override
    public View getView (int position, View convertView, ViewGroup parent)
    {
        Asset asset = getItem(position);

        RelativeLayout layout = (RelativeLayout) LayoutInflater.from(context).inflate(resource, parent, false);

        TextView assetName = (TextView) layout.findViewById(textViewResourceId);
        assetName.setText(asset.toString());

        Switch mainSwitch = (Switch) layout.findViewById(R.id.assetswitch);
        mainSwitch.setEnabled(asset.hasSwitchableMain());


        return layout;
    }
}

package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.ArrayAdapter;
import android.widget.RelativeLayout;
import android.widget.TextView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

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
        RelativeLayout layout = (RelativeLayout) LayoutInflater.from(context).inflate(resource, parent, false);
        TextView assetName = (TextView) layout.findViewById(textViewResourceId);
        assetName.setText(super.getItem(position).toString());

        return layout;
    }
}

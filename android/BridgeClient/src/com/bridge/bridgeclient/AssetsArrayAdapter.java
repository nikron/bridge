package com.bridge.bridgeclient;

import android.content.Context;

import android.widget.ArrayAdapter;

public class AssetsArrayAdapter extends ArrayAdapter<Asset>
{
    public AssetsArrayAdapter(Context context, int resource, int textViewResourceId)
    {
        super(context, resource, textViewResourceId);
    }

    @Override
    public void add(Asset asset)
    {
        super.add(asset);
    }
}

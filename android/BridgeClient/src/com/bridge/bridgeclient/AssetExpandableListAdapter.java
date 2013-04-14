package com.bridge.bridgeclient;

import android.content.Context;

import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseExpandableListAdapter;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;
import java.io.IOException;
import org.apache.http.client.ClientProtocolException;

import java.net.URI;

class AssetExpandableListAdapter extends BaseExpandableListAdapter
{
    private Context context;

    private AssetList assets;

    public AssetExpandableListAdapter(Context context, AssetList assets) 
    {
        super();
        this.context = context;
        this.assets = assets;
    }


    @Override
    public boolean isChildSelectable(int groupPosition, int childPosition)
    {
        return true;
    }

    @Override
    public Object getChild (int groupPosition, int childPosition)
    {
        return assets.get(groupPosition);
    }

    @Override
    public long getChildId(int groupPosition, int childPosition)
    {
        return 0;
    }

    @Override
    public View getChildView(int groupPosition, int childPosition, boolean isLastChild, View convertView, ViewGroup parent)
    {
        return new AssetView(context, assets.get(groupPosition));
    }

    @Override
    public int getChildrenCount(int groupPosition)
    {
        return 1;
    }

    @Override
    public long getGroupId(int groupPosition)
    {
        return groupPosition;
    }

    @Override
    public Object getGroup(int groupPosition)
    {
        return assets.get(groupPosition).getName();
    }

    @Override
    public View getGroupView(int groupPosition, boolean isExpanded, View convertView, ViewGroup parent)
    {
        TextView view = new TextView(context);
        view.setText((String) getGroup(groupPosition));

        return view;
    }

    @Override
    public int getGroupCount()
    {
        return assets.length() ;
    }

    @Override
    public boolean hasStableIds()
    {
        return false;
    }

    public void refresh()
    {
        try {

            assets.refresh();
        }
            catch (JSONException e)
        {
            Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
        } 
            catch (ClientProtocolException e)
        {
            Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
        }
            catch (IOException e)
        {
            Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
        }

        notifyDataSetChanged();
    }
}

package com.bridge.bridgeclient;

import android.content.Context;

import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseExpandableListAdapter;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Iterator;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

import java.io.IOException;
import org.apache.http.client.ClientProtocolException;

class ExpandableDeviceList extends BaseExpandableListAdapter
{
    private Context context;

    private ArrayList<AssetView> devices;

    public ExpandableDeviceList(Context context) {
        super();
        this.context = context;
        this.devices = new ArrayList<AssetView>();
    }


    public boolean isChildSelectable(int groupPosition, int childPosition)
    {
        return true;
    }

    public Object getChild (int groupPosition, int childPosition)
    {
        return devices.get(groupPosition);
    }

    public long getChildId(int groupPosition, int childPosition)
    {
        return 0;
    }

    public View getChildView(int groupPosition, int childPosition, boolean isLastChild, View convertView, ViewGroup parent)
    {
        return devices.get(groupPosition);
    }

    public int getChildrenCount(int groupPosition)
    {
        return 1;
    }

    public long getGroupId(int groupPosition)
    {
        return groupPosition;
    }

    public Object getGroup(int groupPosition)
    {
        return devices.get(groupPosition).name;
    }

    public View getGroupView(int groupPosition, boolean isExpanded, View convertView, ViewGroup parent)
    {
        TextView view = new TextView(context);
        view.setText(devices.get(groupPosition).name);

        return view;
    }

    public int getGroupCount()
    {
        return devices.size();
    }

    public boolean hasStableIds()
    {
        return false;
    }

    public void refresh()
    {
        try {
            String assets = Utility.getURL("http://192.168.0.198:8080/assets");
            JSONObject obj = new JSONObject(assets);
            JSONArray urlArray = obj.getJSONArray("assets_urls");

            JSONObject statusObj;
            String urlOfAsset;
            String assetStr;

            String name;
            String realID;
            String uuid;
            String[][] status;

            devices.clear();

            for (int i = 0; i < urlArray.length(); i++)
            {
                urlOfAsset = urlArray.getString(i);

                assetStr = Utility.getURL(urlOfAsset);
                obj = new JSONObject(assetStr);

                name = obj.getString("name");
                realID = obj.getString("real id");
                uuid = obj.getString("uuid");

                statusObj = obj.getJSONObject("state");
                status = new String[statusObj.length()][2];

                int j = 0;
                Iterator<String> categories = statusObj.keys();
                for (String category; categories.hasNext();)
                {
                    category = categories.next();
                    status[j] = new String[2];
                    status[j][0] = category;
                    status[j][1] = statusObj.getString(category);
                    j++;
                }

                JSONArray actionURLs = obj.getJSONArray("action_urls");
                Action[] actions = new Action[actionURLs.length()];

                for (j = 0; j < actionURLs.length(); j++)
                {
                    actions[j] = new Action(actionURLs.getString(j));
                }

                devices.add(new AssetView(context, urlOfAsset, name, realID, status,  uuid, actions));
            }

            notifyDataSetChanged();

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

    }

}

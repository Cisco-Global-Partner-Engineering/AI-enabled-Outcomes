"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Joel Jose <joeljos@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import defaultdict
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import vManage_auth


class AlarmAnalyzer:
    def __init__(self, alarms_data):
        self.raw_data = alarms_data
        self.df = self._prepare_data()
        
    def _prepare_data(self):
        flattened_data = []
        for alarm in self.raw_data:
            flat_alarm = alarm.copy()
            
            if 'devices' in flat_alarm:
                flat_alarm['system_ips'] = [d.get('system-ip') for d in flat_alarm['devices']]
                del flat_alarm['devices']
                
            if 'values' in flat_alarm:
                for key, value in flat_alarm['values'][0].items():
                    flat_alarm[f'value_{key}'] = value
                del flat_alarm['values']
                
            if 'values_short_display' in flat_alarm:
                del flat_alarm['values_short_display']
                
            flattened_data.append(flat_alarm)
            
        df = pd.DataFrame(flattened_data)
        
        timestamp_columns = ['entry_time', 'cleared_time', 'statcycletime', 'receive_time', 'update_time']
        for col in timestamp_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], unit='ms')
                
        return df
    
    def _convert_timestamp(self, ts):
        """Convert timestamp to string format"""
        if pd.isna(ts):
            return None
        return ts.strftime('%Y-%m-%d %H:%M:%S')
    
    def _remove_nulls(self, d):
        """Recursively remove null values, empty values, and NaN from dictionaries and lists"""
        def is_empty_or_null(v):
            # Handle numpy arrays and pandas Series
            if isinstance(v, (np.ndarray, pd.Series)):
                return False  # Don't filter out arrays/series by default
            # Handle scalar NaN values
            if pd.api.types.is_scalar(v) and pd.isna(v):
                return True
            # Handle None, empty strings, and empty collections
            if v is None or v == '' or (isinstance(v, (dict, list)) and not v):
                return True
            return False
        if isinstance(d, dict):
            return {k: self._remove_nulls(v) for k, v in d.items() 
                if not is_empty_or_null(v)}
        elif isinstance(d, list):
            return [self._remove_nulls(v) for v in d 
                if not is_empty_or_null(v)]
        elif pd.api.types.is_scalar(d) and pd.isna(d):  # Handle scalar NaN values
            return None
        return d
    
    def _reduce_alarms_with_clustering(self, eps=0.1, min_samples=2):
        """
        Type-wise alarm reduction using DBSCAN clustering.
        Each alarm type is clustered separately to prevent mixing of different types.
        
        Parameters:
            eps (float): Maximum distance between two samples for them to be considered in the same cluster.
            min_samples (int): Minimum number of alarms in a cluster.
        Returns:
            dict: Contains reduced alarms and explanations.
        """
        if self.df.empty:
            return {"reduced_alarms": [], "explanations": [], "summary": {}}
        
        # Initialize containers for results
        reduced_alarms = []
        explanations = []
        total_clusters = 0
        
        # Process each alarm type separately
        for alarm_type in self.df['type'].unique():
            # Filter data for current type
            type_df = self.df[self.df['type'] == alarm_type].copy()
            
            # Extract features for clustering
            features = type_df[['entry_time', 'severity', 'component']].copy()
            
            # Convert timestamps to seconds from the first alarm
            features['entry_time'] = (features['entry_time'] - 
                                    features['entry_time'].min()).dt.total_seconds()
            
            # Map severity to numeric values
            severity_mapping = {
                'Critical': 4, 'Major': 3, 'Medium': 2, 'Minor': 1, 'Warning': 0
            }
            features['severity'] = features['severity'].map(severity_mapping).fillna(0)
            
            # Map components to numeric values
            component_mapping = {t: i for i, t in enumerate(features['component'].unique())}
            features['component'] = features['component'].map(component_mapping)
            
            # Normalize features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features[['entry_time', 'component', 'severity']])
            
            # Apply DBSCAN clustering
            dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
            clusters = dbscan.fit_predict(scaled_features)
            
            # Process each cluster in the current type
            unique_clusters = set(clusters)
            total_clusters += len(unique_clusters) - (1 if -1 in unique_clusters else 0)
            
            for cluster_id in unique_clusters:
                if cluster_id == -1:  # Skip noise points
                    continue
                
                # Get alarms in current cluster
                mask = (clusters == cluster_id)
                cluster_alarms = type_df[mask]
                
                # Select representative alarm (highest severity)
                severity_series = cluster_alarms['severity'].map(severity_mapping)
                if severity_series.notna().any():
                    representative_alarm = cluster_alarms.loc[severity_series.idxmax()].to_dict()
                else:
                    representative_alarm = cluster_alarms.iloc[0].to_dict()
                
                # Create explanation
                explanation = {
                    "cluster_id": f"{alarm_type}_{cluster_id}",  # Include type in cluster ID
                    "alarm_type": alarm_type,
                    "representative_alarm": representative_alarm['uuid'],
                    "time_span": {
                        "start": cluster_alarms['entry_time'].min(),
                        "end": cluster_alarms['entry_time'].max()
                    },
                    "severity_distribution": cluster_alarms['severity'].value_counts().to_dict(),
                    "affected_components": cluster_alarms['component'].unique().tolist(),
                    "removed_alarms": cluster_alarms['uuid'].tolist(),
                    "cluster_size": len(cluster_alarms)
                }
                
                reduced_alarms.append(representative_alarm)
                explanations.append(explanation)
        
        # Create summary
        summary = {
            "original_count": len(self.df),
            "reduced_count": len(reduced_alarms),
            "reduction_ratio": (len(self.df) - len(reduced_alarms)) / len(self.df) if len(self.df) > 0 else 0,
            "total_clusters": total_clusters,
            "clusters_by_type": {
                alarm_type: len([e for e in explanations if e["alarm_type"] == alarm_type])
                for alarm_type in self.df['type'].unique()
            }
        }
        
        return {
            "reduced_alarms": reduced_alarms,
            "explanations": explanations,
            "summary": summary
        }

    
    def analyze(self, time_window_seconds=300, use_clustering=False, eps=0.1, min_samples=2):
        if use_clustering:
            reduced = self._reduce_alarms_with_clustering(eps=eps, min_samples=min_samples)
        else:
            reduced = self._reduce_alarms_with_explanation(time_window_seconds)
        
        # Fallback for missing 'summary'
        reduction_summary = reduced.get("summary", {})
        
        analysis_result = {
            "analysis_summary": {
                "total_alarms": len(self.df),
                "unique_components": len(self.df['component'].unique()),
                "unique_systems": len(self.df['system_ip'].unique()),
                "reduction_ratio": reduction_summary.get("reduction_ratio", 0),
                "analysis_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            "alarm_reduction": reduced
        }
        
        return self._remove_nulls(analysis_result)

    
    def _reduce_alarms_with_explanation(self, time_window_seconds):
        """Enhanced alarm reduction with detailed explanation"""
        reduced_alarms = []
        reduction_explanations = []
        
        # Sort alarms by time
        sorted_df = self.df.sort_values('entry_time')
        
        # Group alarms by component and type
        grouped = sorted_df.groupby(['component', 'type'])
        
        total_groups = 0
        total_reduced = 0
        
        for (component, alarm_type), group in grouped:
            current_window = []
            last_alarm_time = None
            group_explanation = {
                "component": component,
                "type": alarm_type,
                "original_count": len(group),
                "windows": []
            }
            
            for _, alarm in group.iterrows():
                # Convert timestamps to strings before adding to dictionary
                alarm_dict = alarm.to_dict()
                for key, value in alarm_dict.items():
                    if isinstance(value, pd.Timestamp):
                        alarm_dict[key] = self._convert_timestamp(value)
                
                if last_alarm_time is None:
                    current_window = [alarm_dict]
                    last_alarm_time = alarm['entry_time']
                else:
                    time_diff = (alarm['entry_time'] - last_alarm_time).total_seconds()
                    
                    if time_diff <= time_window_seconds:
                        current_window.append(alarm_dict)
                    else:
                        if current_window:
                            summary, window_explanation = self._summarize_window_with_explanation(current_window)
                            if summary and window_explanation:  # Only add if not None
                                reduced_alarms.append(summary)
                                group_explanation["windows"].append(window_explanation)
                                total_reduced += len(window_explanation["removed_alarms"]) + 1  # Representative alarm + removed alarms
                        current_window = [alarm_dict]
                    last_alarm_time = alarm['entry_time']
            
            if current_window:
                summary, window_explanation = self._summarize_window_with_explanation(current_window)
                if summary and window_explanation:  # Only add if not None
                    reduced_alarms.append(summary)
                    group_explanation["windows"].append(window_explanation)
                    total_reduced += len(window_explanation["removed_alarms"]) + 1
            
            total_groups += 1
            if group_explanation["windows"]:  # Only add if it has windows
                reduction_explanations.append(group_explanation)
        
        return {
            "reduction_summary": {
                "original_count": len(self.df),
                "reduced_count": len(self.df) - len(reduced_alarms),
                "reduction_ratio": (len(self.df) - len(reduced_alarms))/ len(self.df) if len(self.df) > 0 else 0,
                "time_window_seconds": time_window_seconds,
                "total_groups": total_groups
            },
            "reduction_explanations": reduction_explanations,
            "reduced_alarms": reduced_alarms
        }
    
    def _summarize_window_with_explanation(self, alarms):
        """Create detailed summary of alarm window with explanation"""
        if not alarms:
            return None, None
        
        # Sort by severity
        severity_order = {'Critical': 0, 'Major': 1, 'Minor': 2, 'Warning': 3}
        sorted_alarms = sorted(alarms, key=lambda x: severity_order.get(x['severity'], 99))
        
        base_alarm = sorted_alarms[0].copy()
        
        window_explanation = {
            "time_span": {
                "start": min(a['entry_time'] for a in alarms),
                "end": max(a['entry_time'] for a in alarms)
            },
            "alarm_count": len(alarms),
            "severity_distribution": {s: len([a for a in alarms if a['severity'] == s]) 
                                   for s in set(a['severity'] for a in alarms)},
            "representative_alarm": {
                "uuid": base_alarm['uuid'],
                "severity": base_alarm['severity'],
                "message": base_alarm['message'],
                "reason": "Selected as most severe alarm in the window"
            },
            "removed_alarms": [a['uuid'] for a in alarms if a['uuid'] != base_alarm['uuid']],
            "affected_systems": list(set(a['system_ip'] for a in alarms))
        }
        
        base_alarm['grouped_count'] = len(alarms)
        base_alarm['time_span'] = window_explanation['time_span']
        base_alarm['severity_distribution'] = window_explanation['severity_distribution']
        base_alarm['affected_systems'] = window_explanation['affected_systems']
        base_alarm['removed_alarms'] = window_explanation['removed_alarms']
        
        return base_alarm, window_explanation

def convert_timestamps(obj):
    """Recursively convert pandas.Timestamp and numpy types to JSON-serializable formats."""
    if isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S') if not pd.isna(obj) else None
    elif isinstance(obj, (np.int64, np.float64)):  # Convert numpy types to Python types
        return obj.item()
    elif isinstance(obj, list):
        return [convert_timestamps(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_timestamps(value) for key, value in obj.items()}
    return obj


def analyze_alarms(alarms_file='alarms.json', use_clustering=True, eps=0.1, min_samples=2):
    """
    Main function to analyze alarms and output JSON results.
    """
    with open(alarms_file, 'r') as f:
        alarm_data = json.load(f)
    
    analyzer = AlarmAnalyzer(alarm_data)
    results = analyzer.analyze(use_clustering=use_clustering, eps=eps, min_samples=min_samples)

    # Convert Timestamps in results
    results = convert_timestamps(results)
    
    output_file = 'alarm_analysis_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Analysis results saved to {output_file}")
    return results


# Execute analysis
if __name__ == "__main__":
    results = analyze_alarms('alarms.json')
    #print(json.dumps(results, indent=2))
    
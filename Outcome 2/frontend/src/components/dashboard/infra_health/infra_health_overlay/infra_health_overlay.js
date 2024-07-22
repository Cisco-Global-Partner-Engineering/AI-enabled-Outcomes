import React from 'react';
import './infra_health_overlay.css';

function InfraHealthOverlay(props) {
    const infraHealthData = props?.props?.infra_health || [];

    // Add the missing calculateHealthScore function
    function calculateHealthScore(total, offline) {
        return ((total - offline) / total) * 100;
    }

    return (
        <div className="overlay">

                <div className="close-overlay" onClick={() => props.displayStatus(false)}>
                    Close
                </div>

                <div className="overlay-title">Infrastructure Health</div>

            <div className="content">
                {infraHealthData.map((section, index) => {
                    const { meraki_health, umbrella_health, te_health } = section;

                    return (
                        <React.Fragment key={index}>
                            {meraki_health && (
                                <>
                  
                                        <div className="section-title">Meraki Device Statuses</div>
                 
                                    <table className='health-table'>
                                        <thead>
                                            <tr>
                                                <th colSpan="1">Device Metrics</th>
                                                <th>Metric Value</th>
                                                <th>Details</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <div className="metrics-title">Online Devices</div>
                                                </td>
                                                <td>
                                                    <div className="metrics-body">{meraki_health.total_count - meraki_health.offline_count}</div>
                                                </td>
                                                <td>
                                                <div className="metrics-body">
                                                    {meraki_health.online_details.map((device, index) => (
                                                        <div key={index}>{JSON.stringify(device)}</div>
                                                    ))}
                                                </div>
                                                </td>
                                                </tr>

                                                <tr>
                                                <td>
                                                    <div className="metrics-title">Offline Devices</div>
                                                </td>
                                                <td>
                                                    <div className="metrics-body">{meraki_health.offline_count}</div>
                                                </td>
                                                <td>
                                                <div className="metrics-body">
                                                    {meraki_health.offline_details.map((device, index) => (
                                                        <div key={index}>{JSON.stringify(device)}</div>
                                                    ))}
                                                </div>

                                                </td>
                                                </tr>
                                        
                                        </tbody>
                                    </table>
                                </>
                            )}

                            {umbrella_health && (
                                <>
                                        <div className="section-title">Umbrella Tunnel State Information</div>
                                        <table className='health-table'>
                                        <thead>
                                            <tr>
                                                <th colSpan="1">Device Metrics</th>
                                                <th>Metric Value</th>
                                                <th>Details</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <div className="metrics-title">Total Tunnels</div>
                                                </td>
                                                <td>
                                                    <div className="metrics-body">
                                                        {umbrella_health.status_up + umbrella_health.status_down}
                                                    </div>
                                                </td>
                                                <td> 
                                                <div className="metrics-body">
                                                    {JSON.stringify(umbrella_health.details)}
                                                
                                                </div>

                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <div className="metrics-title">Offline Tunnels</div>
                                                </td>
                                                <td>
                                                    <div className="metrics-body">{umbrella_health.status_down}</div>
                                                </td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </>
                            )}

                            {te_health && (
                                <>
                                        <div className="section-title">ThousandEyes Agent State Information</div>
                            
                                        <table className='health-table'>
                                        <thead>
                                            <tr>
                                                <th colSpan="1">Device Metrics</th>
                                                <th>Metric Value</th>
                                                <th>Details</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>
                                                    <div className="metrics-title">Total Agents</div>
                                                </td>
                                                <td>
                                                    <div className="metrics-body">{te_health.agent_data.length}</div>
                                                </td>
                                                <td>
                                                <div className="metrics-body">
                                                    {JSON.stringify(te_health.agent_data)}
                                                
                                                </div>

                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <div className="metrics-title">Offline Agents</div>
                                                </td>
                                                <td>
                                                    <div className="metrics-body">
                                                        {te_health.agent_data.filter((agent) => agent.agentState !== 'online').length}
                                                    </div>
                                                </td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </>
                            )}
                        </React.Fragment>
                    );
                })}
            </div>
        </div>
    );
}

export default InfraHealthOverlay;
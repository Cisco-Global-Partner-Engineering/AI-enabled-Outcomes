import React from 'react';
import './alert_overlay.css';

const AlertOverlay = (props) => {
    return (
        <div className='ov-body'>
            <div className = 'close-overlay' onClick={() => props.displayStatus(false)}>
                Close
            </div>
            <div className='overlay-title'>
                Alerts
            </div>
            <table className='alert-table'>
                <thead>
                    <tr>
                        <th>Family</th>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {props && props.props && props.props.alerts.map((alert, index) => {
                        return (
                            <React.Fragment key={index}>
                                {alert.meraki_alerts && alert.meraki_alerts.alert_data.map((data, i) => (
                                        <tr key={i}>
                                            <td>Meraki</td>
                                            <td>{data.severity}</td>
                                            <td>{data.type}</td>
                                            <td>
                                                {data.details && data.details.map((detail, j) => (
                                                    <div key={j}>
                                                        MAC: {detail.mac}, Name: {detail.name}, Product Type: {detail.productType}, Serial: {detail.serial}, URL: {detail.url}
                                                    </div>
                                                ))}
                                            </td>
                                        </tr>
                                ))}
                                {alert.umbrella_alerts && alert.umbrella_alerts.alert_data.map((data, i) => (
                                    <tr key={i}>
                                        <td>Umbrella</td>
                                        <td> {data.severity} </td>
                                        <td>{data.type}</td>
                                        <td>
                                            {Object.keys(data.details).map((key, index) => {
                                                const value = data.details[key];
                                                if (typeof value === 'object' && value !== null) {
                                                    return (
                                                        <div key={index}>
                                                            {key}: {JSON.stringify(value)}
                                                        </div>
                                                    );
                                                } else {
                                                    return (
                                                        <div key={index}>
                                                            {key}: {value}
                                                        </div>
                                                    );
                                                }
                                            })}
                                        </td>
                                    </tr>
                                ))}
                                
                                {alert.te_alerts && alert.te_alerts.alert_data.map((data, i) => (
                                    <tr key={i}>
                                        <td>TE</td>
                                        <td>{data.severity}</td>
                                        <td>{data.type}</td>
                                        <td>{data.details}</td>
                                    </tr>
                                ))}
                            </React.Fragment>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

export default AlertOverlay;
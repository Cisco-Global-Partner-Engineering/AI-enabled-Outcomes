import React from 'react';
import './app_health_overlay.css';

function AppHealthOverlay(props) {
  const appHealthData = props?.props?.app_health || [];
  //console.log('appHealthData', appHealthData)

  const meraki_app_health = appHealthData[0]?.meraki_app_health || {};
  const te_app_health = appHealthData[1]?.te_app_health || {};

  return (
    <div className="overlay">
      <div className='close-overlay' onClick={() => props.displayStatus(false)}>
        Close
      </div>
      <div className='overlay-title'>
        Application Health
      </div>

      <div className='content'>
        <div className='section'>
          <div className='section-body'>
            <table className='apphealth-table'>
              <thead>
                <tr>
                  <th>Data Source</th>
                  <th>Avg Score</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Meraki</td>
                  <td>{meraki_app_health.avg_score}</td>
                  <td>{JSON.stringify(meraki_app_health.details)}</td>
                </tr>
                <tr>
                  <td>ThousandEyes</td>
                  <td>{te_app_health.avg_score}</td>
                  <td>{JSON.stringify(te_app_health.details)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AppHealthOverlay;
import './alerts.css';
import { Chart } from "react-google-charts";
import AlertOverlay from './alert_overlay/alert_overlay.js';
import { useState } from "react";


function Alerts(props) {

  const [overlay, viewOverlay] = useState(false)

  let totalCritical = 0;
  let totalWarning = 0;
  let totalInformational = 0;
  
  //console.log("props.data",props.data); // print the value of props.data


  if (Array.isArray(props.data.alerts)) {
    props.data.alerts.forEach(item => {
      const alerts = item.meraki_alerts || item.umbrella_alerts || item.te_alerts;
      if (alerts) {
        totalCritical += alerts.critical;
        totalWarning += alerts.warning;
        totalInformational += alerts.informational;
      }
    });
  }
  //console.log("totalCritical",totalCritical); // print the value of totalCritical
  //console.log("totalWarning",totalWarning); // print the value of totalWarning
  //console.log("totalInformational",totalInformational); // print the value of totalInformational
  const data = [
    ["Alert", "Count"],
    ["Critical", totalCritical],
    ["Warning", totalWarning],
    ["Informational", totalInformational]
  ];

  const options = {
    title: "Alert Notifications",
    pieHole: 0.5,
    is3D: false,
    colors: ['red','orange','green']
  };

  return (
    <div className="alerts">
        <div className = 'card'>
            <div className = 'card-title'>
                ALERTS            
            </div>
            <div className = 'hr'></div>
            <div className = 'chart'>
              <Chart
              chartType="PieChart"
              width="550px"
              height="320px"
              data={data}
              options={options}
              />
            </div>

            <div className = 'hr-footer'></div>
            <div className = 'card-footer' onClick={() => viewOverlay(!overlay)}>
                View More            
            </div>
        </div>

        {
          overlay
          ? 
          <div className='overlay'>
            <AlertOverlay displayStatus = {viewOverlay} props={props.data} style = {{display: 'block'}}/>
          </div>
          :
          <div className='overlay' style = {{display: 'none'}}>
            <AlertOverlay/>
          </div>
        }
       

        
    </div>
  );
}

export default Alerts;

import './app_health.css';
import { Chart } from "react-google-charts";
import { useState } from "react";
import AppHealthOverlay from './app_health_overlay/app_health_overlay';


  
  export const options = {
    title: "Application Health",
    pieHole: 0.5,
    is3D: false,
    colors: ['red','orange','green']
  };

function Apphealth(props) {
  const [appOverlay, setAppOverlay] = useState(false)
  var tmpdata = props.data.app_health;
  var totalpercent = (((tmpdata[0].meraki_app_health.avg_score)+(tmpdata[1].te_app_health.avg_score))/2)*100
  //console.log("app_health totalpercent:",totalpercent)
  if(totalpercent > 100){
    totalpercent = 100
  }
  let criticalScore = 0
  let warningScore = 0
  let healthyScore = 0

  if (totalpercent >= 0 && totalpercent <= 33) {
    criticalScore = totalpercent
  }
  else if (totalpercent > 33 && totalpercent <= 100) {
    warningScore = totalpercent
  }
  else {
    healthyScore = totalpercent
  }



  const data = [
    ["Alert", "Count"],
    ['Critical', criticalScore],
    ['Warning', warningScore],
    ['Healthy', healthyScore]
  ];

  //console.log("app_health data:",data)

  return (
    <div className="app-health">
        <div className = 'card'>
            <div className = 'card-title'>
                APPLICATION HEALTH
            </div>
            <div className = 'hr'></div>
            <div className = 'chart'>
      
            <Chart
            chartType="PieChart"
            width="560px"
            height="320px"
            data={data}
            options={options}
            />
            </div>

            <div className = 'hr-footer'></div>
            <div className = 'card-footer' onClick={() => setAppOverlay(!appOverlay)}>
                View More            
            </div>
        </div>

        {
          appOverlay
          ? 
          <div className='overlay'>
            <AppHealthOverlay displayStatus = {setAppOverlay} props={props.data}style = {{display: 'block'}}/>
          </div>
          :
          <div className='overlay' style = {{display: 'none'}}>
            <AppHealthOverlay/>
          </div>
        }

        
    </div>
  );
}

export default Apphealth;

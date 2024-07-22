import './infra_health.css';
import { Chart } from "react-google-charts";
import { useState } from "react";
import InfraHealthOverlay from './infra_health_overlay/infra_health_overlay';





  export const options = {
    title: "Infrastructure Health",
    pieHole: 0.5,
    is3D: false,
    colors: ['red','orange','green']
  };

function Infrahealth(props) {
  const [infraOverlay, setInfraOverlay] = useState(false)

  //console.log("Infra props.data",props.data); // print the value of props.data
  var tmpdata = props.data.infra_health;
  let merakiHealth = tmpdata[0].meraki_health.infratructure_percentage || 0
  let umbrellaHealth = tmpdata[1].umbrella_health.status_up *100 || 0;
  let teHealth = tmpdata[2].te_health.health_percentage || 0;

  let totalHealthScore = (merakiHealth + umbrellaHealth + teHealth) / 3;

  //console.log("Infra Health Scores:",totalHealthScore,merakiHealth,umbrellaHealth,teHealth);
  var health = ''
  var criticalScore = 0
  var warningScore = 0
  var healthyScore = 0

  if (totalHealthScore >= 0 && totalHealthScore <= 33) {
    health = 'Critical'
    criticalScore = totalHealthScore
  } else if (totalHealthScore > 50 && totalHealthScore <= 100) {
    health = 'Warning'
    warningScore = totalHealthScore
  } else {
    health = 'Healthy'
    healthyScore = totalHealthScore
  }

  const data = [
    ["Health", "Score"],
    ['Critical', criticalScore],
    ['Warning', warningScore],
    ['Healthy', healthyScore]
  ];


  return (
    <div className="infra-health">
        <div className = 'card'>
            <div className = 'card-title'>
                INFRASTRUCTURE HEALTH
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
            <div className = 'card-footer' onClick={() => setInfraOverlay(!infraOverlay)}>
                View More            
            </div>
        </div>

        {
          infraOverlay
          ? 
          <div className='overlay'>
            <InfraHealthOverlay displayStatus = {setInfraOverlay} props={props.data} style = {{display: 'block'}}/>
          </div>
          :
          <div className='overlay' style = {{display: 'none'}}>
            <InfraHealthOverlay/>
          </div>
        }
       

        
    </div>
  );
}

export default Infrahealth;

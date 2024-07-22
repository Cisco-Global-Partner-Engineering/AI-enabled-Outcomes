import './top_threats.css';
import { Chart } from "react-google-charts";
import TopThreatsOverlay from './top_threats_overlay/top_threat_overlay';
import { useState } from "react";

export const data = [
    ["Alert", "Count"],
    ["Ransomware", 311],
    ["Malware", 100],
    ["Phishing", 15],
    ["Other", 4]
  ];
  
  export const options = {
    title: "Top Threats",
    pieHole: 0.5,
    is3D: false,
  };

function TopThreats() {
  const [topThreats, setTopThreats] = useState(false)
  return (
    <div className="top-threats">
        <div className = 'card'>
            <div className = 'card-title'>
                TOP THREATS
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
            <div className = 'card-footer' onClick={() => setTopThreats(!topThreats)}>
                View More            
            </div>
        </div>


        {
          topThreats
          ? 
          <div className='overlay'>
            <TopThreatsOverlay displayStatus = {setTopThreats} style = {{display: 'block'}}/>
          </div>
          :
          <div className='overlay' style = {{display: 'none'}}>
            <TopThreatsOverlay/>
          </div>
        }

        
    </div>
  );
}

export default TopThreats;

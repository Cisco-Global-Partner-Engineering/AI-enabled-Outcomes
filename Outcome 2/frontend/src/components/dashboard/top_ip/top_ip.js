import './top_ip.css';
import { Chart } from "react-google-charts";
import TopIPOverlay from './top_ip_overlay/top_ip_overlay';
import { useState } from "react";

export const data = [
    ["IP", "Count"],
    ["10.0.0.1", 36],
    ["192.168.1.2", 22],
    ["143.11.1.0", 19],
    ["Others", 18]
  ];
  
  export const options = {
    title: "Top IPs",
    pieHole: 0.5,
    is3D: false,
    colors: ['brown', 'blue', 'purple', 'gray']
  };

function TopIp() {
  const [topIp, setTopIp] = useState(false)
  return (
    <div className="top_ip">
        <div className = 'card'>
            <div className = 'card-title'>
                TOP IP
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
            <div className = 'card-footer' onClick={() => setTopIp(!topIp)}>
                View More            
            </div>
        </div>

        {
          topIp
          ? 
          <div className='overlay'>
            <TopIPOverlay displayStatus = {setTopIp} style = {{display: 'block'}}/>
          </div>
          :
          <div className='overlay' style = {{display: 'none'}}>
            <TopIPOverlay/>
          </div>
        }
    </div>
  );
}

export default TopIp;

import './summaries_by_rule.css';
import { Chart } from "react-google-charts";
import SummariesByRule from './summaries_by_rule_overlay/summaries_by_rule_overlay';
import { useState } from "react";

export const data = [
    ["Type", "Count"],
    ["High", 1],
    ["Medium", 0],
    ["Low", 0]
  ];
  
  export const options = {
    title: "Intrusion Activity",
    pieHole: 0.5,
    is3D: false,
    colors: ['red', 'orange', 'green']
  };

function SummariesByIntrusion() {
  const [summariesByRule, setSummariesByRule] = useState(false)

  return (
    <div className="summaries-by-rule">
        <div className = 'card'>
            <div className = 'card-title'>
                INTRUSION ACTIVITY
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
            <div className = 'card-footer' onClick={() => setSummariesByRule(!summariesByRule)}>
                View More            
            </div>
        </div>

        {
          summariesByRule
          ? 
          <div className='overlay'>
            <SummariesByRule displayStatus = {setSummariesByRule} style = {{display: 'block'}}/>
          </div>
          :
          <div className='overlay' style = {{display: 'none'}}>
            <SummariesByRule/>
          </div>
        }
      
    </div>
  );
}

export default SummariesByIntrusion;

import './summaries_by_rule_overlay.css';

function SummariesByRule(props) {

  return (
    <div className= "overlay">
        <div className = 'close-overlay' onClick={() => props.displayStatus(false)}>
            Close
        </div>
        <div className = 'overlay-title'>
            Umbrella Intrusion Activity
        </div>

        <div className = 'content'>

            <div className = 'section'>
                <div className = 'section-body'>
                    <div className = 'device-metrics'>
                        <div className = 'total-devices'>
                            <div className = 'metrics-title'>
                                Type
                            </div>
                            <div className = 'metrics-body'>
                                Intrusion
                            </div>
                            
                        </div>
                        <div className = 'offline-devices'>
                            <div className = 'metrics-title'>
                                Destination IP
                            </div>
                            <div className = 'metrics-body'>
                                10.10.10.1
                            </div>
                        </div>
                        <div className = 'offline-devices'>
                            <div className = 'metrics-title'>
                                Classification
                            </div>
                            <div className = 'metrics-body'>
                                Malicious
                            </div>
                        </div>
                        <div className = 'offline-devices'>
                            <div className = 'metrics-title'>
                                Severity
                            </div>
                            <div className = 'metrics-body'>
                                High
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            
            

        </div>
    </div>
  );
}

export default SummariesByRule;

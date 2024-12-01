import './top_threats_overlay.css';

function TopThreatsOverlay(props) {

  return (
    <div className= "overlay">

        <div className = 'ov-header'>
            <div className = 'close-ov' onClick={() => props.displayStatus(false)}>
                Close
            </div>
            
            <div className = 'ov-title'>
                Alert Notifications
            </div>
            <div className = 'ov-refresh-ts'>
                Last Refresh: 10:00:01, 21 Jan 2024
            </div>
        </div>
        

        <div className = 'ov-body'>
            <div className = 'row labels'>
                <div className = 'label-no'>
                    S.No.
                </div>
                <div className = 'label-threat'>
                    Threat
                </div>
                <div className = 'label-threat-type'>
                    Threat Type
                </div>
                <div className = 'label-count'>
                    Count
                </div>
                <div className = 'label-url label-url-color'>
                    URL
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    1
                </div>
                <div className = 'label-threat'>
                    Wannacry
                </div>
                <div className = 'label-threat-type'>
                    Ransomware
                </div>
                <div className = 'label-count'>
                    13:01:10, 21 Jan 2024
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    1
                </div>
                <div className = 'label-threat'>
                    Wannacry
                </div>
                <div className = 'label-threat-type'>
                    Ransomware
                </div>
                <div className = 'label-count'>
                    13:01:10, 21 Jan 2024
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    1
                </div>
                <div className = 'label-threat'>
                    Wannacry
                </div>
                <div className = 'label-threat-type'>
                    Ransomware
                </div>
                <div className = 'label-count'>
                    13:01:10, 21 Jan 2024
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    1
                </div>
                <div className = 'label-threat'>
                    Wannacry
                </div>
                <div className = 'label-threat-type'>
                    Ransomware
                </div>
                <div className = 'label-count'>
                    13:01:10, 21 Jan 2024
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>
            
        </div>
    </div>
  );
}

export default TopThreatsOverlay;

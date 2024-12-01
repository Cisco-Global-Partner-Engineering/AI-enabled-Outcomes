import './top_ip_overlay.css';

function TopIPOverlay(props) {

  return (
        <div className= "overlay">

        <div className = 'ov-header'>
            <div className = 'close-ov' onClick={() => props.displayStatus(false)}>
                Close
            </div>
            
            <div className = 'ov-title'>
                Umbrella Top IPs
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
                <div className = 'label-ip'>
                    IP Address
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
                <div className = 'label-ip'>
                    10.0.0.1
                </div>
                <div className = 'label-count'>
                    34
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    2
                </div>
                <div className = 'label-ip'>
                    192.168.1.2
                </div>
                <div className = 'label-count'>
                    30
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    3
                </div>
                <div className = 'label-ip'>
                    143.11.1.0
                </div>
                <div className = 'label-count'>
                    18
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>

            <div className = 'row'>
                <div className = 'label-no'>
                    1
                </div>
                <div className = 'label-ip'>
                    10.0.0.1
                </div>
                <div className = 'label-count'>
                    34
                </div>
                <div className = 'label-url label-url-color'>
                    Link
                </div>
            </div>
        </div>
        </div>
  );
}

export default TopIPOverlay;

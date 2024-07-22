import './dashboard.css';
import Alerts from './alerts/alerts.js';
import Apphealth from './app_health/app_health.js'; // adjust the path as necessary
import Infrahealth from './infra_health/infra_health.js';   // adjust the path as necessary
import TopThreats from './top_threats/top_threats.js'; // adjust the path as necessary
import { useState, useEffect, useCallback } from 'react';

const host = 'localhost'; // replace with your host
const port = '5001'; // replace with your port

function Dashboard() {
    const [data, setData] = useState({});
    const [isLoading, setIsLoading] = useState(true);

    const getDashboardAlerts = useCallback(async () => {
        try {
            const response = await fetch(`http://${host}:${port}/data`, {
                method: 'GET',
                headers: {'Content-Type': 'application/json'},
                //mode: 'no-cors' // set the request mode to 'no-cors'
            });
    
            if (!response.ok) {
                console.log('Status:', response.status, 'Status text:', response.statusText);
                throw new Error('Network response was not ok');
            }
    
            const data = await response.json();
            console.log('Data:', data);
            setData(data.data);
            setIsLoading(false);
        } catch (error) {
            console.error('Error:', error);
            setIsLoading(false);
        }
    }, []); // add any dependencies of getDashboardAlerts here

    useEffect(() => {
        getDashboardAlerts();
        const intervalId = setInterval(getDashboardAlerts, 300000); // 300000 ms = 5 minutes

        // Clear the interval when the component unmounts
        return () => clearInterval(intervalId);
    }, [getDashboardAlerts]); // getDashboardAlerts is now a dependency

    if (isLoading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="dashboard">
            <div className="card">
                <Alerts data={data} />
            </div>
            <div className="card">
                <Infrahealth data={data} />
            </div>
            <div className="card">
                <Apphealth data={data} />
            </div> 
            <div className="card">
            <TopThreats data={data} />
            </div>
        </div>
    );
}

export default Dashboard;
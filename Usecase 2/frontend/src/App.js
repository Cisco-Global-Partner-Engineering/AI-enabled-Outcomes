import logo from './logo.svg';
import './App.css';
import cisco_logo from './Cisco-logo.png'
import Dashboard from './components/dashboard/dashboard.js';


function App() {
  return (
    <div className="App">
      <div className = 'nav'>
        <div className = 'logo'>
          <img className = 'logo-img' src = {cisco_logo}/>
        </div>
        <div className = 'nav-label'>
          Cross Platform Analytics
        </div>
      </div>

      <div className = 'dashboard'>
        <Dashboard/>
      </div>
    </div>
  );
}

export default App;

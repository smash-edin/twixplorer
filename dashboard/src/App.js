import './App.css';
import Admin from './components/Admin';
import Login from './components/Login';
import Layout from './components/Layout';
import Analysis from './components/Analysis';
import Help from './components/Help';
import Unauthorized from './components/Unauthorized';
import Missing from './components/Missing';
import { Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import 'semantic-ui-css/semantic.min.css'
import LoadReport from "./components/LoadReport";
//import RequireAuth from './components/RequireAuth'
//import TestPage from "./components/TestPage"; <Route path="/test" element= { <TestPage /> } />


function App() {
  return (
    <>
    <Navbar />
    <Routes>
      <Route path="/" element= { <Layout /> } />
      <Route path="/analysis" element= { <Analysis /> } />
      <Route path="/help" element= { <Help /> } />

      <Route path="login" element= {< Login /> } />
      <Route path="admin" element= {< Admin /> } />
        <Route path="load_report" RequireAuth element= {< LoadReport />}/>
        <Route path="analysis" RequireAuth element= {< Analysis /> } />

      <Route path="unauthorized" element= {< Unauthorized /> } />
      <Route path="*" element= {< Missing /> } />
    </Routes>
    </>
  );
}

export default App;
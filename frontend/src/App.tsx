import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import FixPreview from './pages/FixPreview';
import Callback from './pages/Callback';

const App: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/fix" element={<FixPreview />} />
          <Route path="/callback" element={<Callback />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;

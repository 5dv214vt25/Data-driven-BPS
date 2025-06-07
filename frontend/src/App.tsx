import { Routes, Route } from 'react-router-dom';
import { UserProvider } from './context/userContext';
import { useEffect, useState } from 'react';
import { iAuthentication } from './types/types.tsx';
import { Authentication } from './models/authentication.tsx';

import Home from './pages/Home';
import About from './pages/About';
import Settings from './pages/Settings';
import APIPlayground from './pages/APIPlayground';
import Simulation from './pages/Simulation';
import EventLogs from './pages/EventLogs';
import Discovery from './pages/Discovery.tsx';
import Analysis from './pages/Analysis.tsx';
import Layout from './components/Layout';
import Login from './pages/Login.tsx';
import { LocalAuthService } from './auth/localAuthService.tsx';

import './assets/styles/App.css';
import './assets/styles/fonts.css';

function App() {
  const [authentication, setAuthentication] = useState<iAuthentication | null>(null);
  const [showLogin, setShowLogin] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  /**
   * Fetches local auth if possible
   * Fixes 'bugg' where login.tsx  momentarily renders before it reroutes
   *
   * @function
   */
  useEffect(() => {
    const loadAuthState = async () => {
      // Check if no local auth is set
      if (authentication == null) {
        let storedAuth = LocalAuthService.loadAuth();
        if (storedAuth) {
          setAuthentication(storedAuth);
          return;
        }

        let auth: iAuthentication = new Authentication().getCurrentState();
        setAuthentication(auth);
        return;
      }

      if (isLoading) {
        setIsLoading(false);
      }

      setShowLogin(authentication.authorized ? false : true);
    };

    loadAuthState();
  }, [authentication?.username, authentication?.authorized, isLoading]);

  /**
   * Helps prevent page to momentarily load before different component rerenders
   *
   * @returns {JSX.Element}
   */
  if (isLoading) {
    return <span />;
  }

  /**
   * Login page should be rerendered after local auth is controlled
   *
   * @returns {JSX.Element}
   */
  if (showLogin) {
    return <Login setAuthentication={setAuthentication} />;
  }

  /**
   * Loads after user auth has been controlled.
   *
   * @returns {JSX.Element}
   */
  return (
    <UserProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/Simulation" element={<Simulation />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/api-playground" element={<APIPlayground />} />
          <Route path="/eventlogs" element={<EventLogs />} />
          <Route path="/discovery" element={<Discovery />} />
          <Route path="/about" element={<About />} />
          <Route path="/analysis" element={<Analysis />} />
        </Routes>
      </Layout>
    </UserProvider>
  );
}

export default App;


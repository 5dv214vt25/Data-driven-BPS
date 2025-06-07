import { Button } from '@ui5/webcomponents-react';
import { LocalAuthService } from '../auth/localAuthService';
import { useUser } from "../context/userContext";

import '../assets/styles/AccountInfo.css';

/**
 * Topbar component that presents the current account information
 * Is presented by pressing on the upper right icon. 
 * 
 * @component
 */
function AccountInfo() {

  const { userSettings } = useUser();

  const setInformation = (label: string, value: string | null) => (
    <div className="info-row">
      <span className="info-label">{label}:</span>
      <span className="info-value">{value}</span>
    </div>
  );

  /**
   * Displays the user settings
   * 
   * @returns {JSX.Element}
   */
  return (
    <div className='popupContainer'>
      <div className="accountHeader">
        Account info
      </div>

      {setInformation("Username", userSettings.username)}

      <div style={{ marginTop: '10px' }}></div>
      <Button className='button-login debug-hide-fully' >
        Login
      </Button>

      <Button
        className='button-register debug-hide-fully'>
        Register
      </Button>

      <div style={{ marginTop: '10px' }} />
      <Button
        className='logoutButton'
        onClick={() => {
          LocalAuthService.clearAuth();
          window.location.href = '/';
        }}
      >Logout</Button>
    </div >
  );
}

export default AccountInfo;

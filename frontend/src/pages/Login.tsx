import { useEffect, useRef, useState } from 'react';
import { Button, Input, InputDomRef, Ui5CustomEvent } from '@ui5/webcomponents-react';
import { iAuthentication } from '../types/types';
import { Authentication } from '../models/authentication';
import { LocalAuthService } from '../auth/localAuthService';

import '../assets/styles/Login.css';
import logo from '../assets/logo/logo_design3.png';


/**
 * Props for the authentication-handling component.
 * 
 * @param setAuthentication - Function to update the user's authentication state.
 */
interface Props {
  setAuthentication: (value: iAuthentication) => void;
}

/**
 * Starting and login page for the application
 * Handles to login to the main application
 * 
 * @component
 */
const Login = (param: Props) => {

  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");


  const refUsername = useRef<InputDomRef>(null);
  const refPassword = useRef<InputDomRef>(null);


  /**
   * Fetches local auth if it exists and automatically loads it.
   * 
   * @function
   */
  useEffect(() => {
    refUsername.current?.focus();
    try {
      let storedAuth = LocalAuthService.loadAuth();
      if (storedAuth) {
        param.setAuthentication({ ...storedAuth });
      }
    } catch (error: any) {
      console.error("On trying to read storage: ", error.message);
    }
  }, []);


  /**
   * Displays a popup window if the user tries to enter wrong auth details
   * 
   * @param _username - the string value from the username input box
   * @param _password - the string value from the password input box
   * @function
   */
  const handleSubmit = (_username: string = username, _password: string = password) => {

    let authentication = LocalAuthService.authGetAccount(_username);
    if (_username == "") {
      _username = "guest1";
    }

    if (authentication == undefined) {

      authentication = new Authentication({
        username: _username,
        password: _password,
        authorized: true,
      }).getCurrentState();

    } else {
      authentication.authorized = true;
    }


    param.setAuthentication({ ...authentication });
    try {
      LocalAuthService.saveAuth(new Authentication(authentication));
    } catch (error: any) {
      console.error("Error on Submit:", error.message);
    }
  };

  /**
   * Enables the user to just use 'Enter' to 'click' submit. 
   * 
   * @param event - The key event. 
   * @function
   */
  const handleKeyEvent = (event: any) => {
    let _username: string = "";

    if (event.key == "Enter") {
      if (refUsername.current?.value) {
        _username = refUsername.current.value;
        setUsername(_username);
      }

      if (refPassword.current?.value) {
        setPassword(refPassword.current.value);
      }

      handleSubmit(_username);
    }
  };


  /**
   * Start and login page for the application.
   * Is displayed if the user isn't logged in.
   * 
   * @returns {JSX.Element}
   */
  return (
    <div className="pageContainer">

      <div className="loginBox">
        <div className="logoSection">

          <div className='titleContainer'>
            <img src={logo} className="logoIcon" />
            <div className="headline">- Business Process Simulation</div>
          </div>

          <p className="subHeadline"> Cutting-edge. Open-source. Data-driven.</p>

        </div>
        <div className="loginContainer">
          <h1 className='loginContainer-headline'>Welcome</h1>
          <p className='loginContainer-subHeadline'>Please enter a username</p>

          <Input
            className="username"
            ref={refUsername}
            autoFocus={true}
            placeholder='Username'
            onKeyDown={handleKeyEvent}
            value={username}
            onChange={(e: Ui5CustomEvent<InputDomRef>) => {
              setUsername(e.target.value);
            }}
          />

          <div className='sendBox'>

            <div className='buttonContainer'>
              <Button
                className='signInButton'
                onClick={() => handleSubmit()}>
                Sign in
              </Button>
            </div>

          </div>
        </div>
      </div>
    </div >
  );
};


export default Login;

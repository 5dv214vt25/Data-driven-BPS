
import { iAuthentication } from '../types/types';


/**
 * iAuthenticationClass handles the user authentication data. 
 * 
 */
export interface iAuthenticationClass {
  /**
   * string that holds the holds the users username
   */
  username: string;
  /**
   * string that holds the users password
   */
  password: string;
  /**
   * authorized is a boolean value, if the user should be granted to the website or not.
   */
  authorized: boolean;

  /**
   * checks if the user is authorized or not
   */
  isAuthorized(): boolean;
  /**
   * gets the current user session data. 
   */
  getCurrentState(): iAuthentication;
  /**
   * converts the authenticationClass to a json object.
   */
  toJSON(): string;
}

/**
 * User authentication class that handles the user data
 * 
 */
export class Authentication implements iAuthentication {
  private _username: string;
  private _password: string;
  private _authorized: boolean;

  /**
   * Sets the users username, password, and authorization
   *  
   * @Constructor 
   * 
   * @param username - string of the users username, set to EMPTY if nothing is provided
   * @param password - string of the users password, sets to EMPTY if nothing is provided
   * @param authorized - boolean value if the user is authorized, sets to FALSE if no boolean value is provided. 
   * @return 
   */
  constructor({ username = '', password = '', authorized = false }: Partial<iAuthentication> = {}) {
    this._username = username;
    this._password = password;
    this._authorized = authorized;
  }

  /**
   * Returns the users username
   * 
   * @function
   * 
   * @return the users username
   */
  get username() { return this._username }

  /**
   * sets the user username
   * 
   * @function
   * 
   * @param name string value of the user username (should be atleast 3 characters)
   */
  set username(name: string) {
    if (name.length < 3) {
      throw new Error('Username must be at least 3 characters');
    }
    this._username = name;
  }

  /**
   * checks if the user are authorized to use the webpage.
   * 
   * @function
   * 
   * @param boolean value is the user are authorized or not.
   */
  get authorized() { return this._authorized }

  /**
   * checks if the user are authorized to use the webpage.
   * 
   * @function
   * 
   * @param boolean value is the user are authorized or not.
   */
  public isAuthorized(): boolean {
    return this._authorized
  }

  /**
   * sets the authorization of the user.
   * 
   * @function
   * 
   * @param boolean value is the user are authorized or not.
   * 
   * @returns void
   */
  set authorized(authorized: boolean) {
    this._authorized = authorized;
  }


  /**
   * gets the user password
   * 
   * @function string - users password
   */
  get password() { return this._password }
  /**
   * sets the password
   * 
   * @function
   * 
   * @param password- stirng value that sets the user password
   */
  set password(password: string) {
    this._password = password;
  }

  /**
   * Converts user data into a instance of a class
   * 
   * @function
   * 
   * @param config- full or partial object that matches iAuthentication interface
   * @returns data object that matches the current state of AuthenticationClass
   */
  static create(config: Partial<iAuthentication>): iAuthentication {
    const instance = new Authentication(config);
    return instance.getCurrentState();
  }

  /**
   * Exports all data this is mainly used mostly for state management
   * 
   * @function
   * 
   * @returns data object that matches the current state of AuthenticationClass
   * 
   */
  public getCurrentState(): iAuthentication {
    return {
      username: this._username,
      password: this._password,
      authorized: this._authorized,
    };
  }

  /**
   * Converts the class data to JSON in a verified and safe way
   * 
   * @function
   * 
   * @returns `string` a json representation of the current 
   * instance of AuthenticationClass 
   * 
   */
  public toJSON(): string {
    let currentState: iAuthentication = this.getCurrentState();

    if (Authentication.isIAuthentication(currentState)) {
      return JSON.stringify(currentState);
    }

    throw new Error("Invalid JSON structure for iAuthentication");
  }

  /**
   * Create a Authentication class in a vierifed and safe manner.
   * 
   * @function
   * 
   * @param jsonString - a string of data that matches iAuthentication interface
   * @returns a data object that matches the iAuthentication interface
   * 
   */
  public static setFromJSON(jsonString: string): iAuthenticationClass {
    let parsedData: unknown = JSON.parse(jsonString);

    if (!this.isIAuthentication(parsedData)) {
      throw new Error('Invalid JSON structure for iAuthentication');
    }

    return new Authentication({
      username: parsedData.username,
      password: parsedData.password,
      authorized: parsedData.authorized,
      // userID: parsedData.userID
    });
  }

  /**
   * Verifies that the data is formated correctly and has all the parameters
   * 
   * @param data - Unknown data to be checked.
   * @returns `true` if `data` conforms to `iAuthentication`, `false` otherwise.
   * 
   */
  private static isIAuthentication(data: unknown): data is iAuthentication {
    return (
      typeof data === 'object' && data !== null &&
      'username' in data && typeof data.username === 'string' &&
      'password' in data && typeof data.password === 'string' &&
      'authorized' in data && typeof data.authorized === 'boolean'
    );
  }


}
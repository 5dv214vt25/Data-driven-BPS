import { Authentication, iAuthenticationClass } from "../models/authentication";
import { iAuthentication } from "../types/types";


/**
 * LocalAUthService is a utility class that manages the local authentication logic for user accounts.
 * 
 * @component
 */
export class LocalAuthService {
  // Key used to store/retrieve authentication data in sessionStorage.
  private static _AUTH_KEY = "authentication";

  // Hardcoded list of available accounts with default (unauthorized) state.
  private static _ACCOUNTS: iAuthentication[] = [
    new Authentication({ username: "admin", password: "password", authorized: false }).getCurrentState(),
    new Authentication({ username: "guest", password: "password", authorized: false }).getCurrentState(),
    new Authentication({ username: "guest1", password: "password", authorized: false }).getCurrentState(),
    new Authentication({ username: "guest2", password: "password", authorized: false }).getCurrentState(),
    new Authentication({ username: "guest3", password: "password", authorized: false }).getCurrentState(),
  ];

  static authGetAccounts(): iAuthentication[] {
    return LocalAuthService._ACCOUNTS;
  }

  /**
   * Returns a specific user accoutn
   * 
   * @returns a user account
   */
  static authGetAccount(_user: string): iAuthentication | undefined {
    if (typeof _user === 'string') {
      return this._ACCOUNTS.find(account => account.username === _user);
    }
    return undefined;
  }


  /**
   * Allows the user to save a new user accoutn
   * 
   * @returns a boolean value if a new user account was created.
   */
  static saveAuth(auth: iAuthenticationClass): boolean {
    try {
      const authJSON: string = auth.toJSON();
      sessionStorage.setItem(LocalAuthService._AUTH_KEY, authJSON);
    } catch (error) {
      return false;
    }
    return true;
  }

  /**
   * Loads the user session data from the local storage.
   * 
   * @returns a user account if it exist, else null.
   */
  static loadAuth(): iAuthentication | null {
    const storedAuth: string | null = sessionStorage.getItem(LocalAuthService._AUTH_KEY);
    if (typeof storedAuth == 'string' && storedAuth.trim() !== '') {
      const account: iAuthentication = Authentication.setFromJSON(storedAuth).getCurrentState();
      return account;
    }

    return null;
  }

  /**
   * Removes all the session data from the browser storage. 
   * 
   */
  static clearAuth() {
    sessionStorage.clear();
  }
}

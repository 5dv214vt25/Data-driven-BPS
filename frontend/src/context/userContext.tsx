import React, { createContext, useContext, useState } from 'react';
import { LocalAuthService } from '../auth/localAuthService';

/**
 * Holds all meta data about the user in the local storage.
 *
 * @interface iUserObj
 */
interface iUserObj {
  /**
   * string value that holds the users username
   */
  username: string;
  /**
   * Holds the latest selected eventlog ID.
   */
  selectedEventlogId: string | null;
  /**
   * holds the latest selected scenario ID.
   */
  selectedScenarioId: string | null;
  /**
   * holds the latest selected analys/simulation option 
   */
  selectedApproach: "Simod" | "Agent" | null;
}

/**
 * Holds specific userdata in the context window, for subcomponents on the webpage to use. 
 *
 * @interface UserContextType
 */
interface UserContextType {
  /**
   * Holds all the user settings
   */
  userSettings: iUserObj;
  /**
   * Holds the latest selected eventlog ID.
   */
  setSelectedEventlogId: (id: string | null) => void;
  /**
   * holds the latest selected scenario ID.
   */
  setSelectedScenarioId: (id: string | null) => void;
  /**
   * holds the latest selected analys/simulation option 
   */
  setSelectedApproach: (approach: "Simod" | "Agent" | null) => void;
}

/**
 * Creates a context metadatablock that holds user useful information
 */
const UserContext = createContext<UserContextType | undefined>(undefined);


// UserProvider is a React context provider that supplies user-related state and update functions
// Context provider that supplies user-related states to all child components
export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {

  // Initialize userSettings state using data from local authentication if available.
  // Defaults to guest settings if no stored auth data exists.
  const [userSettings, setUserSettings] = useState<iUserObj>(() => {
    let auth = LocalAuthService.loadAuth();
    return ({
      username: auth?.username ? auth.username : "guest1",
      selectedEventlogId: null,
      selectedScenarioId: null,
      selectedApproach: null, // Added
    });
  });

  // Updates the selected event log ID in userSettings.
  const setSelectedEventlogId = (id: string | null) => {
    setUserSettings((prev) => ({
      ...prev,
      selectedEventlogId: id,
    }));
  };

  // Updates the selected scenario ID in userSettings.
  const setSelectedScenarioId = (id: string | null) => {
    setUserSettings((prev) => ({
      ...prev,
      selectedScenarioId: id,
    }));
  };

  // Updates the selected modeling approach ("Simod", "Agent", or null).
  const setSelectedApproach = (approach: "Simod" | "Agent" | null) => {
    setUserSettings((prev) => ({
      ...prev,
      selectedApproach: approach,
    }));
  };

  // Expose the userSettings and updater functions to any children via context
  return (
    <UserContext.Provider value={{ userSettings, setSelectedEventlogId, setSelectedScenarioId, setSelectedApproach }}>
      {children}
    </UserContext.Provider>
  );
};


// Custom hook to access user context.
// Ensures it is only used within a UserProvider to prevent runtime errors.
export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

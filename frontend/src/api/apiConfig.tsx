/**
 * This file is currently unused (4/5 2025) but can be used in the future,
 * the meaning of the file is to simplify API-calls.
 * 
 * API Endpoint Builder Module
 * 
 * This module defines and manages structured API endpoint URLs,
 * ensuring consistent and type-safe generation of paths and query parameters used 
 * throughout the application when interacting with backend services.
 *
 * ## Features
 * - Enum `ApiEndPoint`: Enumerates all available backend endpoints for Simod, Agent, User, and Event Logs.
 * - `ApiRoutes`: Maps `ApiEndPoint` values to base paths (either `/api` or `/storage`) with descriptive routing.
 * - `params`: Utility functions to build query parameters like `user_id`, `scenario_id`, etc.
 * - `buildURL()`: Helper function to concatenate base routes with URL-encoded query strings.
 * - `endPoint`: Main export providing organized, contextual access to API endpoints grouped by domain:
 *   - `USERS`: Create, retrieve, update, and delete users.
 *   - `EVENT_LOGS`: Upload, fetch, and delete event logs.
 *   - `AGENT`: Perform discovery and simulation, and fetch available scenarios.
 *   - `SIMOD`: Handle discovery, simulation, and scenario management related to Simod workflows.
 */

enum ApiEndPoint {
  // simod
  SIMOD_GET_SCENARIOS,
  SIMOD_UPLOAD_SCENARIO,
  SIMOD_START_SCENARIO,
  SIMOD_START_DISCOVERY,

  //Agent
  LIST_AGENT_SCENARIOS,
  START_AGENT_DISCOVERY,
  START_AGENT_SIMULATION,

  // User
  USER_GET_ALL,
  USER_CREATE,
  USER_GET_ONE,
  USER_UPDATE,
  USER_DELETE,

  // event logs
  EVENT_LOGS_GET_ALL,
  EVENT_LOGS_GET_ONE,
  EVENT_LOGS_UPLOAD,
  EVENT_LOGS_DELETE_ONE,
  EVENT_LOGS_DELETE_ALL,
}

const BasePath = {
  API: "/api",
  STORAGE: "/storage",
} as const;


const ApiRoutes: Record<ApiEndPoint, string> = {
  // SIMOD
  [ApiEndPoint.SIMOD_GET_SCENARIOS]: `${BasePath.STORAGE}/list-simod-scenarios`,
  [ApiEndPoint.SIMOD_UPLOAD_SCENARIO]: `${BasePath.STORAGE}/upload-simod-scenario`,
  [ApiEndPoint.SIMOD_START_SCENARIO]: `${BasePath.STORAGE}/upload-simod-scenario`,
  [ApiEndPoint.SIMOD_START_DISCOVERY]: `${BasePath.API}/start-simod-discovery`,

  // AGENT
  [ApiEndPoint.LIST_AGENT_SCENARIOS]: `${BasePath.STORAGE}/list-agent-scenarios`,
  [ApiEndPoint.START_AGENT_SIMULATION]: `${BasePath.API}/start-agent-simulation`,
  [ApiEndPoint.START_AGENT_DISCOVERY]: `${BasePath.API}/start-agent-discovery`,

  // USER
  [ApiEndPoint.USER_GET_ALL]: `${BasePath.API}/`,
  [ApiEndPoint.USER_CREATE]: `${BasePath.API}/users`,
  [ApiEndPoint.USER_GET_ONE]: `${BasePath.API}/users`,
  [ApiEndPoint.USER_UPDATE]: `${BasePath.API}/users`,
  [ApiEndPoint.USER_DELETE]: `${BasePath.API}/users`,

  // EVENT LOGS
  [ApiEndPoint.EVENT_LOGS_GET_ALL]: `${BasePath.STORAGE}/list-event-logs`,
  [ApiEndPoint.EVENT_LOGS_GET_ONE]: `${BasePath.STORAGE}/get-event-log`,
  [ApiEndPoint.EVENT_LOGS_UPLOAD]: `${BasePath.STORAGE}/upload-event-log`,
  [ApiEndPoint.EVENT_LOGS_DELETE_ONE]: `${BasePath.STORAGE}/delete-event-log`,
  [ApiEndPoint.EVENT_LOGS_DELETE_ALL]: `${BasePath.STORAGE}/delete-all-event-logs`,
};
// interface ApiParams {
type ApiParamBuilder = {
  userID: (userID: string) => string;
  scenarioID: (scenarioID: string) => string;
  eventLogID: (eventLogID: string | string) => string;
  save: (save: boolean) => string;
  name: (name: string) => string;
};

const params: ApiParamBuilder = {
  userID: (userID: string) => `user_id=${encodeURIComponent(userID)}`,
  scenarioID: (scenarioID: string) => `scenario_id=${encodeURIComponent(scenarioID)} `,
  eventLogID: (eventLogID: string | number) => `event_log_id=${encodeURIComponent(eventLogID)} `,
  name: (name: string) => `name=${encodeURIComponent(name)} `,
  save: (save: boolean) => `save_boolean=${save} `,
};



const buildURL = (ApiCall: ApiEndPoint, params: string[] | string) => {
  const baseUrl = ApiRoutes[ApiCall];
  try {
    if (Array.isArray(params)) {
      const queryParams = [...params].join('&');
      return `${baseUrl}?${queryParams}`;
    }
    return `${baseUrl}?${params}`;

  } catch (e: any) {
    console.error(e.message);
  }
};


export const endPoint = {
  USERS: {
    GET_ALL: () => {
      return ApiEndPoint.USER_GET_ALL;
    },

    CREATE: (userID: string) => {
      return buildURL(ApiEndPoint.USER_CREATE, params.userID(userID));
    },

    GET_ONE: (userID: string) => {
      return buildURL(ApiEndPoint.USER_GET_ONE, params.userID(userID));
    },

    UPDATE: (userID: string) => {
      return buildURL(ApiEndPoint.USER_UPDATE, params.userID(userID));
    },

    DELETE: (userID: string) => {
      return buildURL(ApiEndPoint.USER_DELETE, params.userID(userID));
    }
  },

  EVENT_LOGS: {
    // GET_ALL: (userID: string) => `/storage/list-event-logs?user_id=${userID}`,
    GET_ALL: (userID: string) => {
      return buildURL(ApiEndPoint.EVENT_LOGS_GET_ALL, params.userID(userID));
    },

    GET_ONE: (userID: string, eventLogID: string) => {
      return buildURL(ApiEndPoint.EVENT_LOGS_GET_ONE, [
        params.userID(userID),
        params.eventLogID(eventLogID),
      ]);
    },

    // UPLOAD: () => "/storage/upload-event-log",
    UPLOAD: () => { return ApiEndPoint.EVENT_LOGS_UPLOAD; },


    DELETE_ONE: (userID: string, eventLogID: string) => {
      return buildURL(ApiEndPoint.EVENT_LOGS_DELETE_ONE, [
        params.userID(userID),
        params.scenarioID(eventLogID),
      ]);
    },

    DELETE_ALL: (userID: string) => {
      return buildURL(ApiEndPoint.EVENT_LOGS_DELETE_ALL, params.userID(userID));
    },
  },

  AGENT: {
    DISCOVERY: {
      START: (userID: string, eventLogID: string) => {
        return buildURL(ApiEndPoint.START_AGENT_DISCOVERY, [
          params.userID(userID),
          params.scenarioID(eventLogID),
        ]);
      },
    },

    SIMULATION: {
      START: (userID: string, eventLogID: string) => {
        return buildURL(ApiEndPoint.START_AGENT_SIMULATION, [
          params.userID(userID),
          params.scenarioID(eventLogID),
        ]);
      },
    },

    SCENARIOS: {
      // GET_ALL: (userID: string) => `/storage/list-agent-scenarios?user_id=${userID}`,
      GET_ALL: (userID: string) => {
        return buildURL(ApiEndPoint.LIST_AGENT_SCENARIOS, params.userID(userID));
      },
    }
  },

  SIMOD: {
    DISCOVERY: {
      START: (userID: string, eventLogID: string) => {
        return buildURL(ApiEndPoint.SIMOD_START_DISCOVERY, [
          params.userID(userID),
          params.eventLogID(eventLogID),
        ]);
      }
    },

    SIMULATION: {
      START: (userID: string, scenarioID: string, save: boolean) => {
        return buildURL(ApiEndPoint.SIMOD_START_DISCOVERY, [
          params.userID(userID),
          params.scenarioID(scenarioID),
          params.save(save)
        ]);
      }
    },
    SCENARIOS: {
      START_ONE: (userID: string, eventLogID: string) => {
        return buildURL(ApiEndPoint.SIMOD_GET_SCENARIOS, [
          params.userID(userID),
          params.scenarioID(eventLogID),
          params.name("hej")
        ]);
      },

      GET_ALL: (userID: string) => {
        return buildURL(ApiEndPoint.SIMOD_GET_SCENARIOS, params.userID(userID));
      },

      UPLOAD: (userID: string) => {
        return buildURL(ApiEndPoint.SIMOD_UPLOAD_SCENARIO, params.userID(userID));
      },
    }
  },
};


export default endPoint;

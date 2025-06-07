export const Mode = {
  AGENT: "agent",
  ROLE: "role",
  ACTIVITY: "activity"
};

export const ModeFields: any = {
  agent: ['activityDurations', 'timePeriods', 'activities', 'role', 'resourceName'],
  role: ['agents'],
  activity: ['agentsCount', 'agentsWorkingOnActivity'],
};

/* An enum-like structure that makes a conversion between camelCase and 'natural' language */
export const CamelCaseToNatural: { [key: string]: string } = {
  duration: "Duration",
  agentsWorkingOnActivity: "Agents Working On Activity",
  agentsCount: "Number Of Agents Working On Activity",
  maxActivityCount: "Max Activity Count Per Case",
  agentID: "Agent ID",
  activityDurations: "Activity Durations",
  timePeriods: "Time Periods",
  activities: "Activities",
  role: "Role",
  agents: "Agents",
  calendar: "Calendar",
  from: "From",
  to: "To",
  beginTime: "Begin Time",
  resourceName: "New Resource Name",
  endTime: "End Time",
};

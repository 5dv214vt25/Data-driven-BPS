/**
 * Allow the user the configure the Agent simulator.
 * 
 */
export type AgentSimulatorSettings = {
  /**
   * Disables the delay between different agents in Agent. 
   */
  extraneousDelays: boolean;
  /**
   * option between central or distributed architecture on the simulator running. 
   */
  centralOrchestration: boolean;
  /**
   * Setting to allow it to be determined automatically. 
   */
  determineAutomatically: boolean;
};
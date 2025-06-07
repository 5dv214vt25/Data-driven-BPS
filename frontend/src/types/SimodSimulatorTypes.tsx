/**
 * Configuration options for the Simod simulation
 * 
 */
export type SimodSimulatorSettings = {
  /**
   * Disables the delay between different agents in Simod. 
   */
  disableExtraneousDelays: boolean;
  /**
   * Sets a specific algoritm to be used on the extracted data.
   */
  setSplitMinerV1: boolean;
};

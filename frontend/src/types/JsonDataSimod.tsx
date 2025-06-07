/*
 * Type interface for parsing the contents of the JSON parameters file returned
 * by Simod discovery.
 */

export interface JsonDataSimod {
  gateway_branching_probabilities?: GatewayBranchingProbability[];
  task_resource_distribution?: TaskResourceDistribution[];
  resource_profiles?: ResourceProfile[];
}

export interface GatewayBranchingProbability {
  gateway_id: string;
  probabilities: PathProbability[];
}

export interface TaskResourceDistribution {
  task_id: string;
  resources: ResourceDistribution[];
}

export interface PathProbability {
  path_id: string;
  value: number;
}

export interface ResourceDistribution {
  resource_id: string;
  distribution_name: string;
  distribution_params: DistributionParam[];
}

export interface DistributionParam {
  value: number;
}

export interface ResourceProfile {
	id: string;
	name: string;
	resource_list: Resource[];
}

export interface Resource {
	id: string;
	name: string;
	amount: number;
	cost_per_hour: number;
	calendar: string;
	assignedTasks: string[];
}

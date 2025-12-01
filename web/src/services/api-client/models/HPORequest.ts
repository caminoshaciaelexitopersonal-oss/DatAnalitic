/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Payload for the POST /hpo/submit endpoint.
 */
export type HPORequest = {
    /**
     * The job_id of the main analysis pipeline to link with.
     */
    job_id: string;
    /**
     * The name of the model to optimize.
     */
    model_name: string;
    /**
     * The number of HPO trials to run.
     */
    n_trials?: number;
    /**
     * The scoring metric to optimize for.
     */
    scoring?: string;
};

/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Payload for the POST /submit endpoint.
 */
export type AutoMLRequest = {
    /**
     * The job_id of the main analysis pipeline to link with.
     */
    job_id: string;
    /**
     * The target variable for supervised learning. If None, it's inferred from the target detection step.
     */
    target?: (string | null);
    /**
     * Optional list of model keys to run. If None, a default selection is used.
     */
    models_to_run?: (Array<string> | null);
    /**
     * Whether to perform Hyperparameter Optimization.
     */
    perform_hpo?: boolean;
};

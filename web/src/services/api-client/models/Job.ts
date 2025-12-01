/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Step } from './Step';
export type Job = {
    job_id: string;
    session_id: string;
    job_type: string;
    created_at: string;
    status?: string;
    steps?: Array<Step>;
};

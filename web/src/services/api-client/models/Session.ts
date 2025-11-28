/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Job } from './Job';
export type Session = {
    session_id?: string;
    created_at?: string;
    status?: string;
    jobs?: Record<string, Job>;
};

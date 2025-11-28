/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MpaDataGovernanceService {
    /**
     * Get Data Catalog
     * Retrieves the data catalog, showing metadata for all datasets in the system.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDataCatalogUnifiedV1MpaGovernanceCatalogGet(): CancelablePromise<Array<Record<string, any>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/mpa/governance/catalog',
        });
    }
}

/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MpaDataGovernanceService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Data Catalog
     * Retrieves the data catalog, showing metadata for all datasets in the system.
     * @returns any Successful Response
     * @throws ApiError
     */
    public getDataCatalogUnifiedV1MpaGovernanceCatalogGet(): CancelablePromise<Array<Record<string, any>>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/unified/v1/mpa/governance/catalog',
        });
    }
}

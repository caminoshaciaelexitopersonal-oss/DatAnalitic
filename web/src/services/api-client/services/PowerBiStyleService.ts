/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DashboardConfig } from '../models/DashboardConfig';
import type { DataQueryRequest } from '../models/DataQueryRequest';
import type { RecommendationRequest } from '../models/RecommendationRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class PowerBiStyleService {
    /**
     * List Dashboards
     * List all available dashboard IDs.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listDashboardsUnifiedV1WpaPowerbiPowerbiDashboardsGet(): CancelablePromise<Array<string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/powerbi/powerbi/dashboards',
        });
    }
    /**
     * Get Dashboard
     * Returns full dashboard: layout, widgets, filters, metadata.
     * @param dashboardId
     * @returns DashboardConfig Successful Response
     * @throws ApiError
     */
    public static getDashboardUnifiedV1WpaPowerbiPowerbiDashboardDashboardIdGet(
        dashboardId: string,
    ): CancelablePromise<DashboardConfig> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/powerbi/powerbi/dashboard/{dashboard_id}',
            path: {
                'dashboard_id': dashboardId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Query Data
     * Executes a dataset query (SQL-like, pandas-like, or connector).
     * Automatically handles:
     * - DBs
     * - CSV/Excel/Parquet
     * - Google Drive / OneDrive
     * - DataLake
     * - AutoML enriched data
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static queryDataUnifiedV1WpaPowerbiPowerbiDataQueryPost(
        requestBody: DataQueryRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/powerbi/powerbi/data/query',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Widget Data
     * Returns processed widget data (aggregations, group-bys, filters applied).
     * @param dashboardId
     * @param widgetId
     * @param filterValues JSON string of filters
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getWidgetDataUnifiedV1WpaPowerbiPowerbiDataWidgetDashboardIdWidgetIdGet(
        dashboardId: string,
        widgetId: string,
        filterValues?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/powerbi/powerbi/data/widget/{dashboard_id}/{widget_id}',
            path: {
                'dashboard_id': dashboardId,
                'widget_id': widgetId,
            },
            query: {
                'filter_values': filterValues,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Recommend Dashboard
     * AutoML suggestions:
     * - Best KPIs
     * - Best chart types
     * - Best variables to analyze
     * - Insights (correlations, trends)
     * - Feature importance
     * - Clusters / segments
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static recommendDashboardUnifiedV1WpaPowerbiPowerbiModelRecommendPost(
        requestBody: RecommendationRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/unified/v1/wpa/powerbi/powerbi/model/recommend',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Clear Cache
     * Deletes all internal cache for dashboards, widgets and datasets.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static clearCacheUnifiedV1WpaPowerbiPowerbiCacheClearDelete(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/unified/v1/wpa/powerbi/powerbi/cache/clear',
        });
    }
    /**
     * Powerbi Status
     * @returns any Successful Response
     * @throws ApiError
     */
    public static powerbiStatusUnifiedV1WpaPowerbiPowerbiStatusGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/unified/v1/wpa/powerbi/powerbi/status',
        });
    }
}

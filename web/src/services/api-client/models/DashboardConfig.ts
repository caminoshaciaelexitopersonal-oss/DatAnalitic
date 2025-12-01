/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type DashboardConfig = {
    /**
     * Dashboard ID
     */
    id: string;
    /**
     * Human title
     */
    title: string;
    description?: (string | null);
    category?: (string | null);
    global_filters?: (Record<string, any> | null);
    /**
     * Layout: {widgets: [...], grid: {...}}
     */
    layout: Record<string, any>;
};

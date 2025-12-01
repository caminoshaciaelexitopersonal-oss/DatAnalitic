/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import { AuthenticationService } from './services/AuthenticationService';
import { DefaultService } from './services/DefaultService';
import { McpMainControlPlaneService } from './services/McpMainControlPlaneService';
import { MpaAiEthicsService } from './services/MpaAiEthicsService';
import { MpaAiProxyService } from './services/MpaAiProxyService';
import { MpaComplianceService } from './services/MpaComplianceService';
import { MpaDataGovernanceService } from './services/MpaDataGovernanceService';
import { MpaDataQualityService } from './services/MpaDataQualityService';
import { MpaDtlService } from './services/MpaDtlService';
import { MpaIngestionService } from './services/MpaIngestionService';
import { PowerBiStyleService } from './services/PowerBiStyleService';
import { WpaAutomatedAnalysisService } from './services/WpaAutomatedAnalysisService';
import { WpaAutoMlService } from './services/WpaAutoMlService';
import { WpaIntelligentRouterService } from './services/WpaIntelligentRouterService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class ApiClient {
    public readonly authentication: AuthenticationService;
    public readonly default: DefaultService;
    public readonly mcpMainControlPlane: McpMainControlPlaneService;
    public readonly mpaAiEthics: MpaAiEthicsService;
    public readonly mpaAiProxy: MpaAiProxyService;
    public readonly mpaCompliance: MpaComplianceService;
    public readonly mpaDataGovernance: MpaDataGovernanceService;
    public readonly mpaDataQuality: MpaDataQualityService;
    public readonly mpaDtl: MpaDtlService;
    public readonly mpaIngestion: MpaIngestionService;
    public readonly powerBiStyle: PowerBiStyleService;
    public readonly wpaAutomatedAnalysis: WpaAutomatedAnalysisService;
    public readonly wpaAutoMl: WpaAutoMlService;
    public readonly wpaIntelligentRouter: WpaIntelligentRouterService;
    public readonly request: BaseHttpRequest;
    constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? '',
            VERSION: config?.VERSION ?? '1.0',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });
        this.authentication = new AuthenticationService(this.request);
        this.default = new DefaultService(this.request);
        this.mcpMainControlPlane = new McpMainControlPlaneService(this.request);
        this.mpaAiEthics = new MpaAiEthicsService(this.request);
        this.mpaAiProxy = new MpaAiProxyService(this.request);
        this.mpaCompliance = new MpaComplianceService(this.request);
        this.mpaDataGovernance = new MpaDataGovernanceService(this.request);
        this.mpaDataQuality = new MpaDataQualityService(this.request);
        this.mpaDtl = new MpaDtlService(this.request);
        this.mpaIngestion = new MpaIngestionService(this.request);
        this.powerBiStyle = new PowerBiStyleService(this.request);
        this.wpaAutomatedAnalysis = new WpaAutomatedAnalysisService(this.request);
        this.wpaAutoMl = new WpaAutoMlService(this.request);
        this.wpaIntelligentRouter = new WpaIntelligentRouterService(this.request);
    }
}

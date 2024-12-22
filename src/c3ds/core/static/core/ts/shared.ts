export interface WebSocketCommand {
    cmd: string;
    id?: number;
    payload?: string;
    displaySlug?: string;
}

export interface BackdoorResult {
    cmd: 'bdRES',
    id: number;
    reqCmd: string,
    error: string | null;
    result: any;
    pStart: number;
    pEnd?: number | null;
}


export interface WebSocketCommand {
    cmd: string;
    id?: number;
    payload?: string;
    displaySlug?: string;
}

export interface RemoteShellResult {
    cmd: 'rsRES',
    id: number;
    reqCmd: string,
    error: string | null;
    result: any;
    pStart: number;
    pEnd?: number | null;
}

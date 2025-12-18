import {WebSocketCommand, WebSocketClient} from "./websocket.ts";

export interface RemoteShellCommand extends WebSocketCommand{
  cmd: string;
  id?: number;
  payload?: string;
  displaySlug?: string;
}

export interface RemoteShellResult extends WebSocketCommand {
    cmd: 'rsRES',
    id: number;
    reqCmd: string,
    error: string | null;
    result: any;
    pStart: number;
    pEnd?: number | null;
}


export class RemoteShellClient {
  ws: WebSocketClient

  constructor(webSocketClient: WebSocketClient) {
    this.ws = webSocketClient
    this.ws.registerCommand('rsMSG', (cmd) => {
      this.onRemoteShell(cmd as RemoteShellCommand)
    })
  }

  async onRemoteShell(cmd: RemoteShellCommand) {
    if (!cmd.payload || !cmd.id) {
      return;
    }

    let res: RemoteShellResult = {
      cmd: "rsRES",
      reqCmd: cmd.payload,
      id: cmd.id,
      pStart: performance.now(),
      pEnd: null,
      error: null,
      result: null,
    };

    try {
      const r = (0, eval)(cmd.payload);
      if (r instanceof Promise || Object.getPrototypeOf(r).hasOwnProperty('then')) {
        res.result = await r;
      } else {
        res.result = r;
      }

    } catch (e: any) {
      res.error = e.toString();
    }

    res.pEnd = performance.now();

    this.ws.ws?.send(JSON.stringify(res));
  }
}
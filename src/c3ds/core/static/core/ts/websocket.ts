export interface WebSocketCommand {
  cmd: string;
}

export interface ReceivedWebSocketCommand extends WebSocketCommand {
  receiveTimestampe: number;
}

export interface ReloadWebSocketCommand extends ReceivedWebSocketCommand {
  delayed?: boolean
}

export interface websocketMessageCallback { (cmd: ReceivedWebSocketCommand): void }

export class WebSocketClient {
  displaySlug: string
  ws: WebSocket | null = null
  heartbeatInterval: number | null = null
  unansweredPings: number = 0
  callbacks: {[key: string]: websocketMessageCallback} = Object()

  constructor(displaySlug: string, autoconnect: boolean) {
    if (displaySlug === undefined || displaySlug == null) {
      throw Error('display slug missing')
    }
    this.displaySlug = displaySlug
    if (autoconnect) this.connect()
  }

  connect() {
    this.ws = new WebSocket(
      (window.location.protocol === 'https:' ? 'wss://' : 'ws://')
      +`${window.location.host}/ws/display/${this.displaySlug}/`
    )
    this.ws.onopen = () => {
      console.log('opening websocket');
      this.unansweredPings = 0
      this.startTimers()
    }
    this.ws.onmessage = (e) => {
      const timeReceived = performance.now()
      console.log("got data from websocket:", e.data)
      const data: ReceivedWebSocketCommand = JSON.parse(e.data);
      data.receiveTimestampe = timeReceived

      switch (data?.cmd) {
        case 'reload':
          if ((data as ReloadWebSocketCommand).delayed) {
            const timeout = 20 * 1000 * Math.random()
            console.log(`received reload command, reloading in ${timeout/1000} seconds!`)
            window.setTimeout(() => {
              window.location.reload()
            }, timeout)
          } else {
            console.log('received reload command, reloading NOW!')
            window.location.reload()
          }
          break;

        case 'pong':
          this.onPingReply()
          break;

        default:
          if (this.callbacks[data.cmd] !== undefined) {
            this.callbacks[data.cmd](data)
          } else {
            console.error('received unknown websocket cmd', data)
          }
      }
    }
    this.ws.onclose = () => {
      this.reconnect()
    }
  }

  reconnect() {
    this.ws?.close()
    const timeout = 5000 + 2000 * Math.random()
    console.log('WS connection died, reconencting in %d', timeout)
    window.setTimeout(() => {
      this.connect()
    }, timeout)
  }

  startTimers() {
    this.stopTimers()
    this.heartbeatInterval = window.setInterval(() => {
      this.sendPing()
    }, 5000)
  }

  stopTimers() {
    if (this.heartbeatInterval !== null) window.clearInterval(this.heartbeatInterval)
  }

  sendPing() {
    console.log('sending ping')
    this.unansweredPings += 1
    if (this.unansweredPings > 30) window.location.reload()  // reload if we didn't get a pong for 300 sec
    this.ws?.send(JSON.stringify({
      cmd: 'ping'
    }))
  }

  onPingReply() {
    this.unansweredPings = 0
  }

  send_raw(data: (string | ArrayBufferLike | Blob | ArrayBufferView)) {
    this.ws?.send(data)
  }

  send(data: WebSocketCommand) {
    this.ws?.send(JSON.stringify(data))
  }

  registerCommand(command: string, callback: websocketMessageCallback) {
    if (this.callbacks[command] !== undefined) {
      throw Error(`command "${command}" already registered`)
    } else {
      this.callbacks[command] = callback
    }
  }

  unregisterCommand(command: string) {
    delete this.callbacks[command]
  }

}
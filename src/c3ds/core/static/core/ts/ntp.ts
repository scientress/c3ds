import {ReceivedWebSocketCommand, WebSocketClient, WebSocketCommand} from "./websocket.ts";
import moment from "moment";

export interface NTPRequest extends WebSocketCommand{
  cmd: 'NTPRequest'
  localClockTime: number
  sendTimestamp: DOMHighResTimeStamp
}

export interface NTPResponse extends ReceivedWebSocketCommand{
  cmd: 'NTPResponse'
  clientSendTimestamp: DOMHighResTimeStamp
  serverTime: number
}


export class NTPClient {
  ws: WebSocketClient
  syncInterval: number | null = null

  constructor(webSocketClient: WebSocketClient) {
    this.ws = webSocketClient
    this.ws.registerCommand('NTPResponse', (cmd) => {
      this.onNTPResponse(cmd as NTPResponse)
    })
    this.startTimers()
  }

  startTimers() {
    this.stopTimers()
    this.syncInterval = window.setInterval(() =>{
      this.sendNTPRequest()
    }, 5 * 60 * 1000)
  }

  stopTimers() {
    if (this.syncInterval !== null) window.clearInterval(this.syncInterval)
  }

  sendNTPRequest() {
    const payload: NTPRequest = {
      cmd: "NTPRequest",
      localClockTime: Date.now(),
      sendTimestamp: performance.now()
    }
    this.ws.send(payload)
  }

  onNTPResponse(response: NTPResponse) {
    if (!response.clientSendTimestamp || !response.serverTime) {
      console.error('invalid NTP response', response)
      return;
    }
    const serverTime = moment(response.serverTime)
    const roundTripTime = response.receiveTimestampe - response.clientSendTimestamp
    const timeoffset = Date.now() - (response.serverTime + roundTripTime / 2 + performance.now() - response.receiveTimestampe)

    console.log(`Received NTP Response after ${roundTripTime} with server time ${serverTime.toISOString(true)} (an offset of ${timeoffset})`)
  }
}
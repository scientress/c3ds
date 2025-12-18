import moment from 'moment';
import {NTPClient} from "./ntp.ts";

declare const window: Window & typeof globalThis & {
 ntp?: NTPClient
}

(() => {
  const container = document.getElementById('clock')
  if (container === null || container.dataset['dayZero'] === undefined) return
  const dayElement = container.querySelector('p span')
  const timeElement = container.querySelector('p:last-child')
  const offsetElement = document.getElementById('ntp-time-offset')
  const latencyElement = document.getElementById('ntp-latency')
  if (dayElement === null || timeElement === null) return;
  const dayZero = moment(container.dataset['dayZero'])

  const update_time = () => {
    const now = !window.ntp ? moment() : window.ntp.getAdjustedTime()
    dayElement.textContent = now.diff(dayZero, 'days').toString()
    timeElement.textContent = now.format('HH:mm')

    if (offsetElement !== null) offsetElement.textContent = `Time offset: ${window.ntp?.offset?.toFixed(3)}ms`
    if (latencyElement !== null) latencyElement.textContent = `Latency: ${window.ntp?.latency?.toFixed(3)}ms`

    window.setTimeout(() => {
      update_time()
    }, 1000 - now.milliseconds())
  }
  update_time()
})()

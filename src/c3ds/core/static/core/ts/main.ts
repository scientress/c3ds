import videojs from 'video.js';
import 'video.js/dist/video-js.css';

// const displaySlug = document.querySelector('body')?.dataset['displaySlug']

// Video Playback
const video_container = document.getElementById('video')
if (video_container !== null) {
  const video_src = video_container.dataset['src']
  const video_type = video_container.dataset['type']
  if (video_src !== undefined && video_type !== undefined) {
    const player = videojs(video_container, {
      controls: false,
      fill: true,
      loop: true,
    })
    player.src({ src: video_src, type: video_type})
    player.play()?.catch(() => {
      player.muted(true)
      player.play()
    })
  }
}


// websocket stuff

interface WebSocketCommand {
  cmd: string
}

class WebScoketClient {
  displaySlug: string | null
  ws: WebSocket | null = null

  constructor(autoconnect: boolean) {
    this.displaySlug = document.querySelector('body')?.dataset['displaySlug'] || null

    if (autoconnect) this.connect()
  }

  connect() {
    if (this.displaySlug === undefined || this.displaySlug == null) {
      return
    }
    this.ws = new WebSocket(
      '/ws/display/'
      + this.displaySlug
      + '/'
    )
    this.ws.onmessage = (e) => {
      console.log("got data from websocket:", e.data)
      const data: WebSocketCommand = JSON.parse(e.data);
      if (data?.cmd === 'reload') {
        window.location.reload()
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

}

new WebScoketClient(true)

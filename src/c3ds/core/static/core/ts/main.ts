import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import {WebSocketClient} from "./websocket.ts";
import {RemoteShellClient} from "./remote_shell.ts";
import {NTPClient} from "./ntp.ts";

const displaySlug = document.querySelector('body')?.dataset['displaySlug']

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
if (displaySlug !== undefined) {
  console.log('Initializing Websocket Client')
  const ws = new WebSocketClient(displaySlug, true)
  new RemoteShellClient(ws)
  const ntp = new NTPClient(ws)
  window.setTimeout(() =>{
    ntp.sendNTPRequest()
  }, 1000)

  console.log('Client Initialized', ws)
}
